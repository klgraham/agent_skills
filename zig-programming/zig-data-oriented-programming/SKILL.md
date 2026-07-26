---
name: zig-data-oriented-programming
description: Data-oriented programming patterns in Zig 0.16 — SoA transforms, SIMD with @Vector, arena lifecycle, cache-line alignment, existential processing. Use when optimizing Zig code for throughput, designing bulk data pipelines, or refactoring hot loops for cache efficiency.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [zig, data-oriented-design, simd, cache, arena, performance, zig-0.16]
    category: software-development
    related_skills: [zig, zig-mmap-project-template, zig-0.16-stdlib-patterns]
    wiki: [[data-oriented-programming/index]]
---

# Data-Oriented Programming in Zig

Write Zig code that respects the hardware. Design for data flow, not object models.

## When to Use

- Optimizing a hot loop that processes thousands+ of homogeneous items
- Designing bulk data pipelines (ETL, vector search, particle systems)
- Building mmap-friendly data structures for cross-process sharing
- Refactoring pointer-heavy OOP-style code that's cache-miss-bound
- Any time `perf stat -e cache-misses` makes you wince

**Don't reach for this skill** when:
- The code isn't performance-critical (prefer readability)
- You're doing I/O-bound work (network, disk)
- The data set is small (<1000 items — overhead of SoA > benefit)
- You haven't profiled first

## Core Principles

1. **Data transformation is the purpose of any program** (Mike Acton). Design the data layout first, then write the code that transforms it.
2. **Measure, don't guess.** `perf stat -e cache-misses,cache-references,instructions,cycles` before and after every change.
3. **Process in bulk.** Linear scans over contiguous arrays beat pointer-chasing through sparse graphs.
4. **Separate hot from cold.** Don't load fields you won't use in the hot loop.
5. **Delete branches.** Use data separation (existential processing) instead of runtime `if`/`switch`.

Wiki knowledge base: [[data-oriented-programming/index]] covers the philosophy, cache hierarchy, SoA vs AoS, and existential processing in detail.

## Patterns

### 1. Measurement First

Before touching any code, establish a baseline. Without numbers, you're doing religion, not engineering.

```bash
# Cache miss baseline
perf stat -e cache-misses,cache-references,cycles,instructions ./benchmark

# Detailed cache simulation (slow but precise)
valgrind --tool=cachegrind ./benchmark
cg_annotate cachegrind.out.<pid>

# Zig: build with -Doptimize=ReleaseFast for realistic measurements
zig build -Doptimize=ReleaseFast
```

**Zig benchmark harness:**
```zig
const std = @import("std");
const Timer = std.time.Timer;

pub fn benchmark(comptime name: []const u8, iterations: usize, f: fn () void) void {
    var timer = Timer.start() catch @panic("no timer");
    for (0..iterations) |_| f();
    const elapsed = timer.read();
    std.debug.print("{s}: {d:.2} ns/op\n", .{ name, @as(f64, @floatFromInt(elapsed)) / @as(f64, @floatFromInt(iterations)) });
}
```

**Rule**: Never claim "faster" without a benchmark with timings. Never claim "better cache" without `perf stat` numbers.

### 2. SoA Transform

Convert Array-of-Structs to Struct-of-Arrays for hot loops that touch only a subset of fields.

**Before (AoS — cache-hostile for partial access):**
```zig
const Particle = struct {
    position: [3]f32,
    velocity: [3]f32,
    life: f32,
    texture_id: u32,  // cold: only used for rendering
};

particles: std.ArrayList(Particle),  // each Particle is 36 bytes; position+velocity = 24 bytes wasted
```

**After (SoA — cache-friendly):**
```zig
const Particles = struct {
    positions_x: []f32,
    positions_y: []f32,
    positions_z: []f32,
    velocities_x: []f32,
    velocities_y: []f32,
    velocities_z: []f32,
    lifes: []f32,
    texture_ids: []u32,  // only touched during render, not physics

    pub fn init(allocator: std.mem.Allocator, count: usize) !Particles {
        return .{
            .positions_x = try allocator.alloc(f32, count),
            .positions_y = try allocator.alloc(f32, count),
            .positions_z = try allocator.alloc(f32, count),
            .velocities_x = try allocator.alloc(f32, count),
            .velocities_y = try allocator.alloc(f32, count),
            .velocities_z = try allocator.alloc(f32, count),
            .lifes = try allocator.alloc(f32, count),
            .texture_ids = try allocator.alloc(u32, count),
        };
    }

    pub fn deinit(self: *Particles, allocator: std.mem.Allocator) void {
        allocator.free(self.positions_x);
        allocator.free(self.positions_y);
        allocator.free(self.positions_z);
        allocator.free(self.velocities_x);
        allocator.free(self.velocities_y);
        allocator.free(self.velocities_z);
        allocator.free(self.lifes);
        allocator.free(self.texture_ids);
    }
};
```

**Comptime SoA generator** (for when you have many types to transform):

```zig
fn SoA(comptime T: type) type {
    const fields = @typeInfo(T).Struct.fields;
    return struct {
        const Self = @This();
        count: usize,
        // One array per field, keyed by field index
        arrays: [fields.len][]u8, // type-erased; cast on access

        pub fn init(allocator: std.mem.Allocator, count: usize) !Self {
            var arrays: [fields.len][]u8 = undefined;
            inline for (fields, 0..) |field, i| {
                const byte_count = @sizeOf(field.type) * count;
                arrays[i] = try allocator.alloc(u8, byte_count);
            }
            return .{ .count = count, .arrays = arrays };
        }

        pub fn get(self: Self, comptime field_idx: usize, index: usize) *fields[field_idx].type {
            const ptr: [*]fields[field_idx].type = @ptrCast(@alignCast(self.arrays[field_idx].ptr));
            return &ptr[index];
        }

        pub fn deinit(self: *Self, allocator: std.mem.Allocator) void {
            for (self.arrays) |arr| allocator.free(arr);
        }
    };
}
```

**When to use SoA:**
- Hot loop touches <50% of struct fields → SoA wins
- Processing is linear and homogeneous → SoA + SIMD
- Data set > L2 cache size (256KB+) → SoA matters more

**When to stay AoS:**
- All fields accessed together in every iteration
- Struct is ≤2 cache lines (128 bytes) and fits in L1
- Code is not in a hot path (readability > micro-optimization)

### 3. SIMD Batch Processing with @Vector

Zig's `@Vector(N, T)` maps directly to SIMD registers. Combine with SoA for maximum throughput.

**Real pattern from zig-hnsw (`src/vector.zig`):**

```zig
/// Compute Euclidean distance with @Vector(8, f32) — 8-way SIMD.
pub fn euclidean(a: [*]const f32, b: [*]const f32, dim: u16) f32 {
    var sum: f32 = 0;
    var i: u16 = 0;

    // SIMD path: process 8 elements per iteration
    if (dim >= 8) {
        var acc: @Vector(8, f32) = @splat(0);
        while (i + 8 <= dim) : (i += 8) {
            const va: @Vector(8, f32) = a[i..][0..8].*;
            const vb: @Vector(8, f32) = b[i..][0..8].*;
            const diff = va - vb;
            acc += diff * diff;
        }
        // Horizontal sum: @reduce in Zig 0.16, manual for now
        sum += acc[0] + acc[1] + acc[2] + acc[3] + acc[4] + acc[5] + acc[6] + acc[7];
    }

    // Scalar tail
    while (i < dim) : (i += 1) {
        const diff = a[i] - b[i];
        sum += diff * diff;
    }
    return math.sqrt(sum);
}
```

**Vector width selection:**
- `@Vector(4, f32)` — SSE (128-bit). Always available on x86-64.
- `@Vector(8, f32)` — AVX/AVX2 (256-bit). Available on most CPUs post-2013.
- `@Vector(16, f32)` — AVX-512 (512-bit). Server CPUs, some recent desktop.
- Use `comptime` to select width based on target CPU features:
  ```zig
  const simd_width = if (@hasDecl(@import("builtin"), "cpu") and
      std.Target.x86.featureSetHas(builtin.cpu.features, .avx2))
      @Vector(8, f32)
  else
      @Vector(4, f32);
  ```

**Common SIMD operations in Zig:**

| Operation | Zig Code |
|---|---|
| Broadcast scalar to vector | `@splat(value)` |
| Element-wise add/sub/mul/div | `a + b`, `a - b`, `a * b`, `a / b` |
| Horizontal sum | `@reduce(.Add, vec)` (Zig 0.16) |
| Load from slice | `slice[i..][0..N].*` |
| Store to slice | `slice[i..][0..N].* = vec` |
| Compare | `a > b` (returns vector of bools) |
| Select/blend | `@select(bool_vec, a, b)` |

**Pitfall**: `@reduce` with enum literal `.Add` is new in 0.16. If the compiler rejects it, fall back to manual horizontal sum: `acc[0] + acc[1] + ... + acc[7]`.

### 4. Arena Lifecycle Management

Entities created and destroyed in bulk match arena allocators perfectly. No per-object `deinit`, no fragmentation.

```zig
var arena = std.heap.ArenaAllocator.init(allocator);
defer arena.deinit();
const level_alloc = arena.allocator();

// Allocate all level data in one arena
const positions = try level_alloc.alloc([3]f32, entity_count);
const velocities = try level_alloc.alloc([3]f32, entity_count);
const collision_shapes = try level_alloc.alloc(CollisionShape, entity_count);

// Process...
updatePhysics(positions, velocities, dt);

// level_alloc.free() never called — arena.deinit() frees everything
```

**When to use arenas:**
- Load/unload cycles (levels, scenes, batches)
- Request-scoped allocations (HTTP handlers, job workers)
- Temporary computation buffers (sorting scratch space, intermediate results)
- Anywhere lifetime groups naturally: "all of these live until X, then they all die"

**When NOT to use arenas:**
- Long-lived entities with independent lifecycles (they'll leak until arena reset)
- Libraries that don't own their data (caller controls lifetime — pass allocator through)
- Very small allocations (<64 bytes, many individual frees) — arena's bulk-free isn't helping

**Nested arenas pattern** (per-frame within per-level):

```zig
var level_arena = std.heap.ArenaAllocator.init(allocator);
defer level_arena.deinit();

for (0..frame_count) |_| {
    var frame_arena = std.heap.ArenaAllocator.init(level_arena.allocator());
    defer frame_arena.deinit(); // frees frame data, level data persists
    // ... per-frame work ...
}
```

### 5. Cache-Line Alignment

Prevent false sharing in multi-threaded code and ensure hot data fits cache lines.

**Align to cache line (64 bytes on x86-64/ARM):**

```zig
const cache_line = 64;

const AlignedBuffer = struct {
    data: [1024]u8 align(cache_line),
};

const PaddedCounter = struct {
    value: std.atomic.Value(u64) align(cache_line) = std.atomic.Value(u64).init(0),
    _pad: [cache_line - @sizeOf(std.atomic.Value(u64))]u8 = [_]u8{0} ** (cache_line - @sizeOf(std.atomic.Value(u64))),
};

comptime {
    std.debug.assert(@sizeOf(PaddedCounter) == cache_line);
}
```

**Extern structs for precise layout control:**

```zig
const CacheLineNode = extern struct {
    data: [56]u8,  // 56 bytes of hot data
    next: u64,      // 8 bytes → total = 64 = one cache line
};
comptime {
    std.debug.assert(@sizeOf(CacheLineNode) == 64);
}
```

**When alignment matters:**
- Per-thread counters/handles (false sharing kills multi-core scaling)
- Freelist nodes (often accessed in tight allocation loops)
- Hot data that should never split across two cache lines (align to `@sizeOf(T)` rounded up to next power of 2 that's ≥ cache_line)

### 6. Existential Processing (Branch Elimination)

Separate data by state so hot loops contain zero branches.

**Before (branch per element):**
```zig
for (entities.items) |*entity| {
    if (entity.mesh != null) {
        drawMesh(entity.mesh.?, entity.transform);
    }
    if (entity.is_alive) {
        entity.updateAI(dt);
    }
}
// Branch mispredict + loading cold mesh data = slow
```

**After (separate arrays):**
```zig
// These arrays only contain items that need processing
for (renderables.items) |*r| {
    drawMesh(r.mesh, r.transform);
}
for (living_ai.items) |*ai| {
    ai.update(dt);
}
// Zero branches, 100% cache utilization
```

**Table-Driven FSM (Zig):**

```zig
const StateFn = *const fn (data: *anyopaque, dt: f32) StateTransition;

const StateTable = struct {
    states: []StateFn,
    entity_state: []u8,     // state index per entity
    entity_data: []*anyopaque,

    pub fn update(self: *StateTable, dt: f32) void {
        // Process all entities in each state — homogeneous, branchless
        for (0..self.states.len) |state_idx| {
            const state_fn = self.states[state_idx];
            for (self.entity_state, 0..) |entity_state, i| {
                if (entity_state == state_idx) {
                    _ = state_fn(self.entity_data[i], dt);
                }
            }
        }
    }
};
```

## Real-World Example: zig-hnsw

zig-hnsw applies multiple DOD patterns:

| Pattern | Where | Why |
|---|---|---|
| SoA storage | `graph.zig`: node_data, edge_offsets, edge_lengths as separate arrays | Node metadata, edge topology, and vector data have different access patterns |
| SIMD @Vector | `vector.zig`: euclidean(), dot() | Distance computation is the inner loop — 8-way SIMD essential |
| Flat arrays over pointers | Entire codebase: `ArrayListUnmanaged`, no heap pointers in serialized structs | mmap-friendly; no pointer fixup on load |
| External vs internal IDs | `graph.zig`: `ExternalId` (u32) vs `NodeIndex` (u32) | Dense internal indexing for array access; callers use stable external IDs |
| Bulk deallocation | `graph.zig:deinit()` frees all arrays in sequence | No per-node alloc/free; predictable, fragmentation-free |

Key lesson: the graph is an HNSW — a pointer-chasing data structure by nature — but zig-hnsw flattens it into arrays so the hot path (distance computation + neighbor traversal) stays contiguous.

## Pitfalls

### Premature optimization
- Don't SoA-transform code that isn't in a hot path. The readability cost is real.
- Don't SIMD-ify loops that run 100 times/frame. The scalar version is fine.
- **Always profile first.** `perf stat` before and after.

### Comptime blowup
- Generating SoA layouts via comptime for types with 50+ fields can blow up compile times.
- Keep comptime type generation focused: generate only what's needed for the hot path.
- If `zig build` hangs or takes >5s for a single type, fall back to explicit SoA.

### @Vector portability
- `@Vector(8, f32)` requires AVX on x86-64. SSE-only CPUs (pre-2011) will scalarize.
- ARM NEON is `@Vector(4, f32)`. Use comptime feature detection.
- `@reduce` enum literal syntax changed in 0.16. Test that your Zig version supports it.

### Alignment gotchas
- `@ptrCast(@alignCast(...))` will compile but crash at runtime if alignment is wrong.
- `std.ArrayList` doesn't guarantee alignment > `@alignOf(T)`. For cache-line alignment, use `allocator.alignedAlloc`.
- `align(N)` on struct fields only works with `extern struct`. Regular structs may reorder.

### Arena leaks
- Forgetting `defer arena.deinit()` leaks everything allocated in the arena.
- Nested arenas: child arena's `deinit()` only frees child arena's metadata, not the data. The data lives in parent arena. Call `child_arena.deinit()` to release metadata.
- Long-running arenas grow unboundedly. For persistent state, use a general-purpose allocator.

### False sharing
- Two atomic counters on the same cache line: `ThreadPool` with per-thread task counts in an array of `u64` — adjacent counters are 8 bytes apart, 8 of them per cache line → massive false sharing. Pad each counter to 64 bytes.

### Existential processing maintenance cost
- Separate arrays require manual synchronization: when an entity dies, remove from `living_ai` array. When it gains a mesh, add to `renderables`.
- For systems with frequent state changes, maintain dirty flags and rebuild separated arrays once per frame rather than updating incrementally.

## Verification Checklist

After applying DOD patterns, verify:

- [ ] `perf stat -e cache-misses,cache-references` shows reduced miss rate
- [ ] Benchmark shows measurable improvement (not noise — run >100 iterations)
- [ ] Correctness: same inputs produce same outputs (write a property test)
- [ ] `zig build test` passes with `-Doptimize=ReleaseFast` and `-Doptimize=Debug`
- [ ] No undefined behavior under valgrind: `valgrind ./benchmark`
- [ ] SIMD fallback path works: test on a CPU without AVX (or set `--test-cpu baseline`)
- [ ] Arena lifecycle: `defer arena.deinit()` is present and correct
- [ ] No alignment assertions firing at runtime (ReleaseSafe build)
- [ ] README updated: explain the data layout so future readers understand why it's flat arrays, not objects

## Related Skills

- [[zig]] — General Zig 0.16 development, build system, stdlib patterns
- [[zig-mmap-project-template]] — mmap-friendly library design with flat binary formats
- [[zig-0.16-stdlib-patterns]] — HTTP, filesystem, SIMD, and other stdlib APIs
- Wiki: [[data-oriented-programming/index]] — Full conceptual background
