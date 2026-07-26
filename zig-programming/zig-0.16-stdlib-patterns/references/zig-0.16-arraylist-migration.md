# Zig 0.16 ArrayListUnmanaged Migration Guide

## What changed

In Zig 0.16, `std.ArrayListUnmanaged` is now an alias, not a distinct struct:

```zig
// Zig 0.15 (and earlier):
// std.ArrayListUnmanaged(T) had fields: { items, capacity }

// Zig 0.16:
pub const ArrayListUnmanaged = ArrayList;  // from std.zig
// ArrayList(T) has fields: { items, capacity, allocator }
```

The unmanaged-only struct (no allocator) no longer exists as a separate type in the stdlib.

## How to detect the problem

```bash
zig build test 2>&1 | grep "missing struct field"
# src/graph.zig:40:27: error: missing struct field: items
```

This error means somewhere a `ArrayListUnmanaged` is being initialized with `.{}` (zero-initialization), which doesn't provide the `allocator` field that the managed version requires.

## Where this bites

### 1. Struct field initialization (most common)

```zig
// BROKEN in 0.16:
const Graph = struct {
    node_data: std.ArrayListUnmanaged(NodeMeta),
    vector_data: std.ArrayListUnmanaged(f32),
    edge_offsets: std.ArrayListUnmanaged(u32),
    ...
    pub fn init(...) !Self {
        return Self{
            .node_data = .{},      // ERROR: missing allocator
            .vector_data = .{},    // ERROR
            ...
        };
    }
};
```

Fix:
```zig
// CORRECT in 0.16:
return Self{
    .node_data = .empty,
    .vector_data = .empty,
    .edge_offsets = .empty,
    ...
};
```

### 2. Local variable initialization

```zig
// BROKEN in 0.16:
var candidates = std.ArrayListUnmanaged(Candidate){};  // ERROR

// CORRECT in 0.16:
var candidates: std.ArrayListUnmanaged(Candidate) = .empty;
```

### 3. Type aliases in structs

```zig
// Common pattern in graph/data-structure code:
pub const EdgeList = std.ArrayListUnmanaged(NodeIndex);
pub const LayerAdjacency = std.ArrayListUnmanaged(EdgeList);

// Both EdgeList and LayerAdjacency are now MANAGED types (have allocator).
// Any .{} initialization of fields typed as these will fail.
```

## The `.empty` literal

`.empty` is the 0.16 shorthand for zero-initialized managed arrays:

```zig
var list: ArrayListUnmanaged(i32) = .empty;
// Equivalent to:
var list: ArrayListUnmanaged(i32) = .{ .items = &[_]i32{}, .capacity = 0 };
// allocator field is set to undefined (correct for unmanaged — not used)
```

## Complete fix pattern (real example from zig-hnsw)

```diff
// graph.zig:37-46  (Graph.init)
pub fn init(allocator: mem.Allocator) !Self {
    return Self{
        .allocator = allocator,
-       .node_data = .{},
-       .construction_layers = .{},
-       .edge_offsets = .{},
-       .edge_lengths = .{},
-       .edge_data = .{},
+       .node_data = .empty,
+       .construction_layers = .empty,
+       .edge_offsets = .empty,
+       .edge_lengths = .empty,
+       .edge_data = .empty,
    };
}

// graph.zig:235  (ensureLayerCountForNodeCount)
-   var layer_adj = LayerAdjacency{};
+   var layer_adj: LayerAdjacency = .empty;

// graph.zig:126-132  (compactEdges)
-   var new_offsets = std.ArrayListUnmanaged(u32){};
-   var new_lengths = std.ArrayListUnmanaged(u32){};
-   var new_edges = std.ArrayListUnmanaged(NodeIndex){};
+   var new_offsets: std.ArrayListUnmanaged(u32) = .empty;
+   var new_lengths: std.ArrayListUnmanaged(u32) = .empty;
+   var new_edges: std.ArrayListUnmanaged(NodeIndex) = .empty;

// index.zig:45-47  (HnswIndex.init)
-       .vector_data = .{},
-       .vector_offsets = .{},
-       .external_to_internal = .{},
+       .vector_data = .empty,
+       .vector_offsets = .empty,
+       .external_to_internal = .empty,

// layer.zig:28,79
-   var candidates = std.ArrayListUnmanaged(Candidate){};
+   var candidates: std.ArrayListUnmanaged(Candidate) = .empty;
```

## Other 0.16 compiler strictness changes

### `var` → `const` lint

Zig 0.16 is stricter about mutability:

```zig
// BROKEN in 0.16:
var copy = try allocator.dupe(u64, samples);  // error: local variable is never mutated

// CORRECT in 0.16:
const copy = try allocator.dupe(u64, samples);
```

Fix: change `var` to `const` for any variable that is never written after initialization. The compiler catches this even in test code.

### Exhaustive switch on unions

When a new field is added to a `union(enum)`, every `switch (value)` must handle it:

```zig
// If Value union gains a `.vector` field:
switch (v) {
    .string => |s| ...,
    .integer => |i| ...,
    // .vector MISSING → error: switch must handle all possibilities
}

// Fix: add the missing arm
switch (v) {
    .string => |s| ...,
    .integer => |i| ...,
    .vector => try writer.writeAll("\"vector\":\"<omitted>\""),
}
```

This is especially common in serialization code (JSON, MsgPack) that pattern-matches on `Value` unions.

## Why this matters for mmap-friendly code

The original appeal of `ArrayListUnmanaged` was that it had no hidden allocator — you could serialize the `{ items, capacity }` fields directly to disk. The managed `ArrayList` still exposes `.items` and `.capacity` publicly; the `allocator` field is only used at runtime for mutations. So the mmap-friendly flat-array pattern still works — you just can't use `.{}` zero-init anymore.

## Related stdlib changes in 0.16

| Old | New | Notes |
|-----|-----|-------|
| `std.ArrayListUnmanaged` (unmanaged) | `std.ArrayListUnmanaged` = `std.ArrayList` (managed) | Breaking |
| `std.ArrayListAlignedUnmanaged` | `std.ArrayListAlignedUnmanaged` = `std.array_list.Aligned` | Deprecated alias |
| `std.Io` | `std.io` | Case change in module name **— but `std.Io` namespace is still present in 0.16, do NOT assume it was removed** |
| `std.http.Client.fetch` (1 arg) | `std.http.Client.fetch(allocator, options)` | allocator now first arg |
| `std.heap.GeneralPurposeAllocator` | `std.heap.DebugAllocator` | Renamed in 0.16; same leak-detection behavior |
| `@intCast` for type coercion | `@as(T, value)` | `@intCast` still exists for int-to-int only |

## Probe: confirm ArrayListUnmanaged is managed in your stdlib

```bash
grep "pub const ArrayListUnmanaged" ~/.local/lib/zig/std/std.zig
# Should show: pub const ArrayListUnmanaged = ArrayList;
```

If it shows a distinct struct definition (pre-0.16 behavior), you're on an older Zig.
