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

See [Manage allocation](../playbooks/manage-allocation.md) for allocating APIs,
transactional updates, and arena reset boundaries.

## Sources

The [allocator guidance](https://ziglang.org/documentation/0.17.1/#Choosing-an-Allocator)
provides the language reference's starting choices. Inspect `std/heap.zig`,
`std/heap/arena_allocator.zig`, `std/heap/debug_allocator.zig`, and
`std/testing.zig` in the pinned installation for contracts and diagnostics.
