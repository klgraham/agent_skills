# Choosing and using an allocator

Choose from the caller's lifetime and memory budget before comparing speed.
An allocator handle borrows its backing allocator state. Returning a handle
from a local arena or moving an allocator after taking that handle can leave
it pointing at dead or moved storage.

## Decision table

| Workload | Starting choice | Contract to check |
|---|---|---|
| Reusable library | Accept `std.mem.Allocator` | Caller chooses policy; returned owner states how to free |
| Process entry point | `init.gpa` from `std.process.Init` | Borrow it; do not deinitialize infrastructure owned by startup |
| Allocating unit test | `std.testing.allocator` | Release owned memory so the test can detect leaks |
| Independent allocations with diagnostics | `std.heap.DebugAllocator(.{})` | Keep allocator state alive; inspect the `deinit` result |
| One bounded scratch phase | `std.heap.FixedBufferAllocator` | Buffer outlives users; budget includes alignment and allocation order |
| Request or batch dies together | `std.heap.ArenaAllocator` over a supplied backing allocator | No escaped views after reset; close non-memory resources separately |
| Measured multithreaded allocation bottleneck | Evaluate `std.heap.smp_allocator` | Compare actual sizes, contention, peak memory, and diagnostic tradeoffs |
| C allocation contract | Library's allocator/free pair, or `std.heap.c_allocator` when appropriate | libc linkage does not make every C library allocation compatible |
| Page-sized backing storage | `std.heap.page_allocator` | Account for granularity and system calls before using for small objects |

Do not select an arena merely to silence leak reports. A long-lived process
arena can retain every abandoned allocation. A child arena over another arena
may retain its backing pages until the parent resets.

## Playbook: implement an allocating API

1. Decide whether the result borrows input or owns a copy. Put that in the API.
2. Choose caller-provided output, a fixed-size value, or heap allocation based
   on the result's bound and lifetime.
3. Put `errdefer` immediately after each successful acquisition. Keep rollback
   active only until ownership transfers.
4. Use one allocator instance consistently. Preserve length and alignment
   information required by its free operation.
5. For collections, reserve before taking interior views, or reacquire views
   after growth. `const` on a slice does not stabilize its backing allocation.
6. Exercise all allocation failure points with `std.testing.checkAllAllocationFailures`.
   Check that a failed mutation leaves the documented old state usable.

Run [ownership.zig](../examples/ownership.zig) for a two-allocation owner,
replacement rollback, nested lists, and an exhausted fixed buffer.

## Playbook: choose an arena reset boundary

List every view retained by the next phase, worker, and callback. Transfer the
needed data to longer-lived storage or finish those consumers before reset.
Use a backing allocator that can reclaim pages if per-batch release matters.
Choose retention limits from measured peak memory. Test repeated batches,
including an unusually large one, instead of checking only final deinit.

## Sources

The [allocator guidance](https://ziglang.org/documentation/0.16.0/#Choosing-an-Allocator)
provides the language reference's starting choices. Inspect `std/heap.zig`,
`std/heap/arena_allocator.zig`, `std/heap/debug_allocator.zig`, and
`std/testing.zig` in the pinned installation for contracts and diagnostics.
