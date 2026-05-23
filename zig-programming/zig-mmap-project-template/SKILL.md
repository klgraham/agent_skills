---
name: zig-mmap-project-template
description: Create a new Zig 0.16 library with mmap-friendly flat-file storage. Template and patterns for zero-copy memory-mapped data structures.
version: 1.0.0
author: Hermes Agent
tags: [zig, mmap, data-structures, template]
category: software-development
---

# Zig mmap Library Template

Create a new Zig library project designed for memory-mapped file storage with flat binary formats.

## Project Setup

### 1. Initialize Repository

```bash
gh repo create zig-<name> --private
git clone https://github.com/klgraham/zig-<name>.git ~/dev/zig-<name>
cd ~/dev/zig-<name>
```

### 2. build.zig.zon (Zig 0.16+)

```zig
.{
    .name = .zig_<name>,
    .version = "0.1.0",
    .fingerprint = 0x<generate-with-zig>,
    .paths = .{
        "build.zig",
        "build.zig.zon",
        "src",
        "LICENSE",
        "README.md",
    },
}
```

To get the fingerprint: put a placeholder `0x0`, run `zig build`, then use the suggested value.

### 3. build.zig (Zig 0.16)

```zig
const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const mod = b.addModule("zig_<name>", .{
        .root_source_file = b.path("src/lib.zig"),
        .target = target,
        .optimize = optimize,
    });

    const lib = b.addLibrary(.{
        .name = "zig_<name>",
        .root_module = mod,
        .linkage = .static,
    });

    b.installArtifact(lib);

    const tests = b.addTest(.{ .root_module = mod });
    const test_step = b.step("test", "Run tests");
    test_step.dependOn(&b.addRunArtifact(tests).step);
}
```

**Key Zig 0.16 changes from 0.13:**
- `addStaticLibrary` → `addLibrary` with `.linkage = .static`
- Use `b.addModule` then `b.addLibrary(.root_module = mod)` pattern
- `standardOptimizeOption` replaces `mode`

### 4. File Layout

```
src/
├── lib.zig         # Public API + re-exports
├── foo.zig         # Core implementation
└── serialize.zig   # mmap save/load
```

## mmap File Format Design

### Header Structure

```zig
pub const Header = extern struct {
    magic: u32,           // Unique identifier (e.g., 'HNSW')
    version: u16,
    // ... other metadata
    reserved: [N]u8,      // Pad to known size
};
```

Use `comptime` assertions to verify sizes:

```zig
comptime {
    std.debug.assert(@sizeOf(Header) == EXPECTED_SIZE);
}
```

### Memory Layout Principles

1. **No pointers in structs** — use offsets into byte arrays
2. **Fixed-width primitives** — u32/u64 for offsets and lengths
3. **Contiguous arrays** — store all data in flat buffers
4. **Separate mutable build layout from mmap snapshot layout** — flat offset tables are excellent for read-only mmap, but dangerous for dynamic variable-length mutation unless offsets are stable or fully updated

```
┌─────────────────────┐
│ Fixed-size Header   │
├─────────────────────┤
│ Data Section 1      │  (e.g., vectors)
├─────────────────────┤
│ Data Section 2      │  (e.g., node metadata)
├─────────────────────┤
│ Variable Data       │  (flattened edges, etc.)
└─────────────────────┘
```

For graph/index structures, prefer:
- Runtime construction: mutable adjacency/segment lists or fixed-capacity per-node slots
- Snapshot/save: compact into flat `offsets[]`, `lengths[]`, `data[]`
- mmap load: read-only slices over the compact format

Avoid inserting into the middle of a shared flat `data[]` buffer unless every later offset is updated; otherwise all subsequent slices become corrupt.

### Public IDs vs Dense Internal Indices

For mmap-friendly graph/vector indexes, do not let caller-facing IDs double as array indices unless the public API explicitly requires dense `0..n-1` IDs. Split identity into two types:

```zig
pub const ExternalId = u32; // caller-facing, serialized, returned by search
pub const NodeIndex = u32;  // dense internal index: 0..node_count-1
```

Use `NodeIndex` for all flat-array indexing and graph topology:

- `vector_offsets.items[node_index]`
- `edge_offsets.items[node_index]`
- `edge_lengths.items[node_index]`
- edge lists storing neighbor `NodeIndex` values
- entry points and layer/search candidates

Store the caller ID only at API boundaries and metadata:

```zig
pub const NodeMeta = struct {
    external_id: ExternalId,
    level: u8,
    vector_offset: u32,
};
```

For mutable indexes, keep a map in the top-level index, not in the graph core:

```zig
external_to_internal: std.AutoHashMapUnmanaged(ExternalId, NodeIndex),
```

Insert pattern:

1. Reject duplicate external IDs: `if (map.contains(id)) return error.DuplicateExternalId;`
2. Allocate `node_index = graph.nodeCount()`.
3. Append vector data and `vector_offsets[node_index]`.
4. Insert graph metadata with both `node_index` and `external_id`.
5. Put `external_id -> node_index` in the map.
6. Use only `node_index` from this point inward.

Search pattern:

1. Layer/search candidates carry `node_index`, not `id`.
2. Compute distances through `vector_offsets.items[node_index]`.
3. Convert back at the API boundary: `SearchHit.id = graph.node_data.items[node_index].external_id`.

Regression tests should use sparse external IDs, e.g. insert `100`, `5000`, `42`, search near `5000`, and assert returned ID `5000`. Add a duplicate-ID test expecting `error.DuplicateExternalId`.

Serialization can keep the compact metadata record if `ExternalId` remains `u32`; write `external_id` in the node metadata table and rebuild the runtime hash map on mutable load if needed.

### HNSW / Multi-Layer Graph Edge Storage

For HNSW-like mmap graph indexes, node `level` metadata is not topology. The edge identity is:

```text
(level, source_node) -> [destination_node...]
```

Do not implement a single `getEdges(node)` graph and pass `level` through call sites while ignoring it. That creates a single-layer graph with random node levels, not HNSW.

Minimal mutable construction layout:

```zig
pub const EdgeList = std.ArrayListUnmanaged(NodeIndex);
pub const LayerAdjacency = std.ArrayListUnmanaged(EdgeList);

construction_layers: std.ArrayListUnmanaged(LayerAdjacency), // [level][node]
edge_offsets: std.ArrayListUnmanaged(u32),                   // compact slot table
edge_lengths: std.ArrayListUnmanaged(u32),
edge_data: std.ArrayListUnmanaged(NodeIndex),
```

Public graph APIs should require a layer so incorrect callers fail at compile time:

```zig
pub fn getEdges(self: *const Self, level: u8, node_index: NodeIndex) []const NodeIndex
pub fn addEdge(self: *Self, level: u8, src: NodeIndex, dst: NodeIndex) !void
pub fn addBidirectionalEdge(self: *Self, level: u8, a: NodeIndex, b: NodeIndex) !void
pub fn hasEdge(self: *const Self, level: u8, src: NodeIndex, dst: NodeIndex) bool
```

Compact with rectangular slots:

```zig
slot = @as(usize, level) * @as(usize, node_count) + @as(usize, node_index);
```

Snapshot format implications:
- Add `layer_count` to the file header and bump format `version`.
- Size edge offset/length tables as `node_count * layer_count`, not `node_count`.
- Empty `(level,node)` slots are fine: offset points at current `edge_data.len`, length is `0`.
- `isCompacted()` should validate every slot and reject any edge where either endpoint has `NodeMeta.level < level`.
- Tests must prove level separation directly: an edge at layer 0 must not appear at layer 1.

### Save Function Pattern

```zig
pub fn saveFile(index: anytype, path: []const u8) !void {
    _ = @TypeOf(index);  // Accept any struct with expected fields
    const file = try fs.cwd().createFile(path, .{ .truncate = true });
    defer file.close();

    // Write header
    var header = Header{...};
    try file.writeAll(mem.asBytes(&header));

    // Write data sections
    try file.writeAll(mem.sliceAsBytes(index.data));
}
```

### Load Function Pattern

```zig
pub const LoadedData = struct {
    handle: MmapHandle,
    header: *const Header,
    // ... slices into mmap'd data
};

pub fn loadFile(_allocator: mem.Allocator, path: []const u8) !LoadedData {
    _ = _allocator;  // mmap doesn't use allocator
    const file = try fs.cwd().openFile(path, .{ .mode = .read_only });
    defer file.close();

    const file_size = try file.getEndPos();
    const data = try mmap(null, file_size, .{ .type = .shared }, file.handle, 0);
    errdefer std.os.munmap(data);

    // Validate header
    const header = @as(*const Header, @ptrCast(data[0..HEADER_SIZE].ptr));
    if (header.magic != EXPECTED_MAGIC) return error.InvalidMagic;

    // Parse sections...
    return LoadedData{...};
}
```

## Common Pitfalls

1. **Fingerprint error**: Zig 0.16 requires valid fingerprint. Use `0x0` placeholder, build, use suggested value.
2. **Unused parameters**: Prefix with `_` or use `var`/`const` with underscore: `_allocator`
3. **Struct field ordering**: `extern struct` fields cannot be reordered; use explicit byte offsets
4. **Tail vectors**: When slicing remaining data, ensure bounds checking: `data[offset..][0..remaining]`
5. **`ArrayListUnmanaged` Zig 0.16 breaking change**: `std.ArrayListUnmanaged` is now an alias for the managed `std.ArrayList` (with `allocator` field). Any `.{ }` zero-init of `ArrayListUnmanaged` fields fails with `error: missing struct field: items`. Replace all `.{ }` with `.empty`. This affects every `Graph.init`, `HnswIndex.init`, `compactEdges`, and local `ArrayListUnmanaged` variables. See `zig-0.16-stdlib-patterns` → `references/zig-0.16-arraylist-migration.md`.
6. **Nested `ArrayListUnmanaged` cleanup**: If runtime construction uses `ArrayListUnmanaged(ArrayListUnmanaged(T))`, deinit every inner list before deiniting the outer list. If rolling back a just-appended inner list, Zig 0.16 `pop()` returns an optional, so use `var inner = outer.pop().?; inner.deinit(allocator);`.
6. **Flat read path after mutable adjacency changes**: If `getEdges()` reads compact flat arrays but `addEdge()` mutates construction adjacency, call `compactEdges()` before any search/serialization that depends on `getEdges()`. Minimal safe pattern is compact once after each node insertion; faster later pattern is make construction-time search read adjacency directly and compact only before snapshot/save.
7. **Serialization stale-flat guard**: For graph snapshots, add a cheap `isCompacted()` invariant check and assert it in `saveFile()` so stale flat `offsets/lengths/data` never silently hit disk.

## Test Pattern

Make the aggregate build test prove something. In Zig libraries, `zig build test` can be a false green if it only tests `src/lib.zig` and that file does not import the integration tests.

Wire important test files explicitly in `build.zig` or import them from the root module:

```zig
const tests = b.addTest(.{ .root_module = mod });
const test_step = b.step("test", "Run tests");
test_step.dependOn(&b.addRunArtifact(tests).step);

const integration_tests_mod = b.createModule(.{
    .root_source_file = b.path("src/my_integration_test.zig"),
    .target = target,
    .optimize = optimize,
});
const integration_tests = b.addTest(.{ .root_module = integration_tests_mod });
test_step.dependOn(&b.addRunArtifact(integration_tests).step);
```

Zig 0.16 pitfall: `std.Build.TestOptions` does not accept `.root_source_file` directly. Create a private module with `b.createModule(...)`, then pass it as `.root_module` to `b.addTest(...)`.

Also run targeted tests when reviewing/debugging:

```bash
zig build test
zig test src/lib.zig
zig test src/serialize.zig
zig test src/my_integration_test.zig
```

```zig
const testing = std.testing;
test "serialize roundtrip" {
    var index = try MyIndex.init(testing.allocator, .{});
    defer index.deinit();

    try index.insert(1, some_vector);

    try saveFile(index, "test.bin");
    const loaded = try loadFile(testing.allocator, "test.bin");
    defer loaded.handle.unmap();

    try testing.expectEqual(index.count(), loaded.header.node_count);
}
```
