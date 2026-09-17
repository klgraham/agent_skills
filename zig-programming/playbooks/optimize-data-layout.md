# Data layout and SIMD in Zig 0.16.0

Use when profiling identifies a compute, allocation, or memory-access bottleneck.
Keep the scalar implementation as a correctness oracle and benchmark baseline.

## Principles

Optimize the data touched by the hot operation. Compare AoS, SoA, and batched
layouts against the actual access pattern. A SoA layout can reduce unused-field
loads but adds coordination work when whole records move or change state.

Prefer explicit typed arrays or `std.MultiArrayList` before a custom type-erased
SoA generator. Preserve rollback, allocator alignment, and initialization proofs
when allocating multiple arrays. Reacquire views after growth or compaction.

`@Vector` describes vector operations, not a guaranteed machine instruction.
Choose widths using measurements and the deployment CPU baseline. In 0.16.0,
LLVM loop vectorization is disabled due to a compiler regression. This makes
inspection of generated code especially useful; it does not make every explicit
vector faster. See the [release notes](https://ziglang.org/download/0.16.0/release-notes.html).

## Playbook: optimize a kernel

1. Fix the workload, input distribution, compiler, target CPU, and shipping mode.
   Measure the full operation as well as the candidate kernel.
2. Identify allocation, cache misses, arithmetic, or branch cost using a profiler.
3. Change one representation or kernel at a time. Include layout conversion
   and dispatch overhead in the full-operation measurement.
4. Compare output with the scalar implementation. Define floating-point tolerance,
   NaN, infinity, overflow, and reproducibility behavior before changing reductions.
5. Repeat measurements enough to characterize noise. Keep the simpler version
   when the gain does not justify maintenance or extra storage.

On Linux, `perf stat` or Cachegrind can help. On macOS use Instruments or
`xctrace`. A benchmark must consume results and vary runtime input enough to
avoid constant folding or dead-code elimination. For 0.16 timing, inspect
`std.Io.Clock` and `std.Io.Timestamp`; do not copy old `std.time.Timer` recipes.

## Playbook: add SIMD safely

Use slices with an explicit equal-length check. Advance a `usize` index over
complete vectors, then process a scalar tail. Bound the vector loop with
`len - i >= width` after establishing `i <= len`; a narrow `i + width` can
overflow before the comparison.

[simd.zig](../examples/simd.zig) tests a dot product at zero length, both
sides of a vector boundary, multiple widths, and mismatched lengths.

| Operation | Form |
|---|---|
| Broadcast | `@splat(value)` with a known vector result type |
| Horizontal sum | `@reduce(.Add, values)` |
| Conditional lane selection | `@select(f32, mask, yes_values, no_values)` |
| Load full array into vector | `slice[i..][0..width].*` |
| Compile-target vector width hint | Inspect `std.simd.suggestVectorLength(T)` |

A compile-target feature check is not runtime CPU detection. For one binary
covering several CPU feature levels, use a tested baseline kernel and explicit
runtime dispatch to compatible specialized kernels. Do not build a portable
release with `-mcpu=native` by accident. Do not raise alignment with a cast
unless the allocation and offset prove it.

## Playbook: change layout or batch by state

Measure which fields are read together. Try a typed SoA or hot/cold split when
that removes significant traffic. For state batching, include the cost of
maintaining membership and rebuilding batches. Queue state changes until an
iteration boundary if immediate mutation would invalidate the current views.

Keep sparse public IDs distinct from dense indices. If deletion reuses slots,
use generations or another stale-handle check. Flat index arrays are not a
promise that positions remain stable under compaction.

## Allocators and false sharing

Use arenas for a phase that actually ends. Close files and foreign handles
before bulk memory cleanup. For repeated batches, a child arena over a growing
parent may retain memory; use a reclaiming backing allocator when required.
Read [allocator choices](../principles/allocators.md) for the decision table.

For independent per-thread counters, measure false sharing and choose padding
from the target cache characteristics. `extern struct` defines ABI layout; it
does not by itself align an allocation to a cache line. Check stride and actual
alignment, plus synchronization and shutdown ordering.

## Verify

Run scalar-equivalence and boundary tests in Debug, ReleaseSafe, and the shipping
mode. Check the baseline target and any specialized CPU targets. Report timings,
variance, workloads, and memory cost. Do not claim speedup from vector syntax or
compilation alone.

Sources: [vectors](https://ziglang.org/documentation/0.16.0/#Vectors),
`std/simd.zig`, `std/multi_array_list.zig`, and the pinned backend's output.

For CPU work split across tasks, read [task concurrency and parallelism](../references/io-concurrency.md). Choose bounded workers and a backend that can execute them on multiple threads, then measure. `io.concurrent` establishes progress requirements; it does not prove SIMD or multicore speedup.
