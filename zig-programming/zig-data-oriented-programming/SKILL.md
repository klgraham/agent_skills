---
name: zig-data-oriented-programming
description: Data-oriented programming patterns in Zig 0.16 — SoA transforms, SIMD with @Vector, arena lifecycle, cache-line alignment, existential processing. Use when optimizing Zig code for throughput, designing bulk data pipelines, or refactoring hot loops for cache efficiency.
license: MIT
metadata:
  hermes:
    tags: [zig, data-oriented-design, simd, cache, arena, performance, zig-0.16]
    category: software-development
    related_skills: [zig, write-legible-zig, zig-memory-safety-review, zig-mmap-project-template, zig-0.16-stdlib-patterns]
    wiki: [[data-oriented-programming/index]]
---

# Data-Oriented Programming in Zig

Write Zig code that respects the hardware. Design for data flow, not object models.

## When to Use

- Optimizing a hot loop that processes thousands+ of homogeneous items
- Designing bulk data pipelines (ETL, vector search, particle systems)
- Building mmap-friendly data structures for cross-process sharing
- Refactoring pointer-heavy OOP-style code that's cache-miss-bound
- Any time the target profiler shows a hot, cache-sensitive path

**Don't reach for this skill** when:
- The code isn't performance-critical (prefer readability)
- You're doing I/O-bound work (network, disk)
- The data set or hot loop is too small for the layout and maintenance cost to matter; measure instead of using a fixed item-count cutoff
- You haven't profiled first

## Core Principles

1. **Data transformation is the purpose of any program** (Mike Acton). Design the data layout first, then write the code that transforms it.
2. **Measure, don't guess.** Use a platform-appropriate profiler before and after every change. On Linux this may be `perf` or Cachegrind; on macOS use Instruments or `xctrace`; record the target, workload, and measurement noise.
3. **Process in bulk.** Linear scans over contiguous arrays beat pointer-chasing through sparse graphs.
4. **Separate hot from cold.** Don't load fields you won't use in the hot loop.
5. **Delete branches.** Use data separation (existential processing) instead of runtime `if`/`switch`.

Wiki knowledge base: [[data-oriented-programming/index]] covers the philosophy, cache hierarchy, SoA vs AoS, and existential processing in detail.

## Patterns

### 1. Measurement First

Before touching any code, establish a baseline. Without numbers, you're doing religion, not engineering.

```bash
# Linux cache-miss baseline
perf stat -e cache-misses,cache-references,cycles,instructions ./benchmark

# Linux detailed cache simulation (slow but precise)
valgrind --tool=cachegrind ./benchmark
cg_annotate cachegrind.out.<pid>

# On macOS, use Instruments or xctrace with the same benchmark workload.

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

**Rule**: Never claim "faster" without benchmark timings. Never claim "better cache" without measurements from a profiler appropriate to the target platform.

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
// The examples in this section assume: const std = @import("std");
const Particles = struct {
    allocator: std.mem.Allocator,
    positions_x: []f32,
    positions_y: []f32,
    positions_z: []f32,
    velocities_x: []f32,
    velocities_y: []f32,
    velocities_z: []f32,
    lifes: []f32,
    texture_ids: []u32,  // only touched during render, not physics

    pub fn init(allocator: std.mem.Allocator, count: usize) !Particles {
        const positions_x = try allocator.alloc(f32, count);
        errdefer allocator.free(positions_x);
        const positions_y = try allocator.alloc(f32, count);
        errdefer allocator.free(positions_y);
        const positions_z = try allocator.alloc(f32, count);
        errdefer allocator.free(positions_z);
        const velocities_x = try allocator.alloc(f32, count);
        errdefer allocator.free(velocities_x);
        const velocities_y = try allocator.alloc(f32, count);
        errdefer allocator.free(velocities_y);
        const velocities_z = try allocator.alloc(f32, count);
        errdefer allocator.free(velocities_z);
        const lifes = try allocator.alloc(f32, count);
        errdefer allocator.free(lifes);
        const texture_ids = try allocator.alloc(u32, count);
        errdefer allocator.free(texture_ids);

        return .{
            .allocator = allocator,
            .positions_x = positions_x,
            .positions_y = positions_y,
            .positions_z = positions_z,
            .velocities_x = velocities_x,
            .velocities_y = velocities_y,
            .velocities_z = velocities_z,
            .lifes = lifes,
            .texture_ids = texture_ids,
        };
    }

    /// Release all arrays with the allocator captured by `init`.
    /// Do not use the slices after this call; they are reset to empty.
    pub fn deinit(self: *Particles) void {
        self.allocator.free(self.positions_x);
        self.allocator.free(self.positions_y);
        self.allocator.free(self.positions_z);
        self.allocator.free(self.velocities_x);
        self.allocator.free(self.velocities_y);
        self.allocator.free(self.velocities_z);
        self.allocator.free(self.lifes);
        self.allocator.free(self.texture_ids);
        self.positions_x = &[_]f32{};
        self.positions_y = &[_]f32{};
        self.positions_z = &[_]f32{};
        self.velocities_x = &[_]f32{};
        self.velocities_y = &[_]f32{};
        self.velocities_z = &[_]f32{};
        self.lifes = &[_]f32{};
        self.texture_ids = &[_]u32{};
    }
};
```

`Particles` owns every slice, captures its allocator, and uses one `errdefer`
per completed allocation so later allocation failure rolls back safely.

**Comptime SoA generator** (for when you have many types to transform):

```zig
fn SoA(comptime T: type) type {
    const fields = @typeInfo(T).@"struct".fields;
    const max_alignment = comptime blk: {
        var alignment: usize = 1;
        for (fields) |field| {
            alignment = @max(alignment, @alignOf(field.type));
        }
        break :blk alignment;
    };
    return struct {
        const Self = @This();
        allocator: std.mem.Allocator,
        count: usize,
        // One type-erased array per field, all using the common maximum
        // alignment so the allocator's free contract remains intact.
        arrays: [fields.len][]align(max_alignment) u8,

        pub fn init(allocator: std.mem.Allocator, count: usize) !Self {
            var arrays: [fields.len][]align(max_alignment) u8 = undefined;
            var initialized: usize = 0;
            errdefer {
                for (arrays[0..initialized]) |array| allocator.free(array);
            }
            inline for (fields, 0..) |field, i| {
                const byte_count = @sizeOf(field.type) * count;
                arrays[i] = try allocator.alignedAlloc(
                    u8,
                    std.mem.Alignment.fromByteUnits(max_alignment),
                    byte_count,
                );
                initialized += 1;
            }
            return .{ .allocator = allocator, .count = count, .arrays = arrays };
        }

        /// Borrow a field value until `deinit`; this type never resizes arrays.
        pub fn get(self: *const Self, comptime field_idx: usize, index: usize) *fields[field_idx].type {
            // The common alignment is at least the field's alignment.
            const ptr: [*]fields[field_idx].type = @ptrCast(self.arrays[field_idx].ptr);
            return &ptr[index];
        }

        pub fn deinit(self: *Self) void {
            for (self.arrays, 0..) |array, i| {
                self.allocator.free(array);
                const empty: *align(max_alignment) [0]u8 = @alignCast(@constCast(&[_]u8{}));
                self.arrays[i] = empty[0..];
            }
        }
    };
}
```

The common `alignedAlloc` preserves typed-access and matching-`free` alignment
for the type-erased arrays; the captured allocator must remain valid through `deinit`.

**When to use SoA:**
- Hot loop touches a small subset of struct fields → SoA may win; measure the working set
- Processing is linear and homogeneous → SoA + SIMD
- The working set exceeds the relevant target cache → SoA may matter more; do not assume a universal L2 size

**When to stay AoS:**
- All fields accessed together in every iteration
- All fields are accessed together and the struct fits comfortably in the target cache hierarchy
- Code is not in a hot path (readability > micro-optimization)

### 3. SIMD Batch Processing with @Vector

Zig's `@Vector(N, T)` expresses element-wise vector operations. The compiler
may lower them to SIMD instructions or scalar code depending on the target,
backend, optimization mode, and operation. Combine them with SoA only after
measurement shows that the layout and vector width help.

**Real pattern from zig-hnsw (`src/vector.zig`):**

```zig
const std = @import("std");
const math = std.math;

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
- Start with a width supported by the target baseline, then benchmark it.
- Do not equate a vector width with a guaranteed instruction set: lowering is target- and backend-dependent.
- Use `comptime` to select a width from the compilation target, not as runtime CPU detection:
  ```zig
  const builtin = @import("builtin");
  const simd_width = if (builtin.cpu.arch == .x86_64 and builtin.cpu.has(.x86, .avx2))
      @Vector(8, f32)
  else
      @Vector(4, f32);
  ```

For one binary that must run across different runtime CPUs, keep target-
specific kernels behind a runtime dispatch boundary and test the baseline
path. Do not treat this compile-time selection as a hardware probe.

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

**Align to a target cache line (often 64 bytes, but verify the target ABI):**

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
- Hot data that should not split across cache lines; use target-specific measurements rather than assuming one cache-line size

### 6. Existential Processing (Branch Elimination)

Separate data by state so the hot loop contains no per-entity classification
branch. The maintenance cost is paid when entities change state.

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
const StateFn = *const fn (data: *anyopaque, dt: f32) void;

const StateBatch = struct {
    state_fn: StateFn,
    // Borrowed: the owner must keep this array and its entity data alive
    // through `StateTable.update` and rebuild the batches after state changes.
    entities: []const *anyopaque,
};

const StateTable = struct {
    // Borrowed batch storage; `update` does not resize or retain it.
    batches: []const StateBatch,

    pub fn update(self: *const StateTable, dt: f32) void {
        // Process homogeneous batches; state classification happened earlier.
        for (self.batches) |batch| {
            for (batch.entities) |entity_data| {
                batch.state_fn(entity_data, dt);
            }
        }
    }
};
```

If a state function needs to request a transition, queue that request and
rebuild the batches after the update pass. Do not reintroduce an entity-state
branch into the hot loop just to make transitions immediate.

## Real-World Example: zig-hnsw

`zig-hnsw` uses flat arrays, separate external/internal IDs, bulk cleanup, and
vectorized distance kernels. Treat those as measured design examples, not
universal claims about every graph workload.

## Pitfalls

### Premature optimization
- Don't SoA-transform code that isn't in a hot path. The readability cost is real.
- Don't SIMD-ify loops that run 100 times/frame. The scalar version is fine.
- **Always profile first.** Use `perf`, Instruments, `xctrace`, or the target's equivalent before and after.

### Comptime blowup
- Generating SoA layouts via comptime for types with 50+ fields can blow up compile times.
- Keep comptime type generation focused: generate only what's needed for the hot path.
- If `zig build` hangs or takes >5s for a single type, fall back to explicit SoA.

### @Vector portability
- A vector type does not by itself promise a particular instruction set or runtime speed. Verify generated code and benchmark the target.
- Use compile-time target features for separate kernels; use a runtime dispatch boundary when one binary must support multiple CPU feature sets.
- `@reduce` enum literal syntax changed in 0.16. Test that your Zig version supports it.

### Alignment and layout gotchas
- `@ptrCast(@alignCast(...))` will compile but crash at runtime if alignment is wrong.
- `std.ArrayList` does not guarantee alignment beyond the element type; use `allocator.alignedAlloc` and retain the proof in the type or its owning abstraction.
- Use `extern struct` when ABI layout is required; regular structs may choose their field layout, so assert the properties the algorithm actually depends on.

### Arena leaks
- Forgetting `defer arena.deinit()` leaks everything allocated in the arena. Nested child arenas free their metadata; parent arenas own the data.
- Long-running arenas grow unboundedly. For persistent state, use a general-purpose/debug allocator appropriate to the project.

### False sharing and existential-processing maintenance
- Two atomic counters on the same cache line: `ThreadPool` with per-thread task counts in an array of `u64` — adjacent counters are 8 bytes apart, 8 of them per cache line → massive false sharing. Pad each counter to 64 bytes.
- Separate arrays require manual synchronization: when an entity dies, remove from `living_ai` array. When it gains a mesh, add to `renderables`.
- For systems with frequent state changes, maintain dirty flags and rebuild separated arrays once per frame rather than updating incrementally.

## Verification Checklist

- [ ] A platform-appropriate profiler (Linux `perf`/Cachegrind, macOS Instruments/`xctrace`, or equivalent) shows a meaningful target-metric change
- [ ] Benchmark shows measurable improvement with enough repetitions to characterize noise, and a property test preserves correctness
- [ ] `zig build test` passes with `-Doptimize=ReleaseFast` and `-Doptimize=Debug`
- [ ] If available, Valgrind or sanitizer instrumentation reports no new issue, and the SIMD fallback works under the project baseline target
- [ ] Arena lifecycle: `defer arena.deinit()` is present and correct
- [ ] Multi-allocation initializers roll back partial success with `errdefer` or an equivalent owner
- [ ] Allocator pairing, borrowed lifetimes, and invalidation rules are documented for public data structures
- [ ] No alignment assertions firing at runtime (ReleaseSafe build)
- [ ] `zig fmt --check` (or the repository formatter) and `git diff --check` pass
- [ ] If a public layout changed, documentation explains why it is flat arrays rather than objects

## Related Skills

`zig` routes general work; `write-legible-zig` covers structure and verification; `zig-memory-safety-review` covers ownership and invalidation; `zig-mmap-project-template` covers flat storage; `zig-0.16-stdlib-patterns` covers runtime APIs; the wiki provides broader DOD background.
