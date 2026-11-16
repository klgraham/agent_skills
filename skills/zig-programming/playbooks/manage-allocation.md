# Manage allocation and ownership

Read [allocator selection](../principles/allocators.md) for storage choices
and [error handling](../principles/error-handling.md) for rollback invariants.

## Implement an allocating API

1. Decide whether the result borrows input or owns a copy. Put that in the API.
2. Choose caller-provided output, a fixed-size value, or heap allocation based
   on the result's bound and lifetime.
3. Register `errdefer` after each acquisition and before the next. Return the
   final owner after all acquisitions succeed.
4. Use one allocator instance consistently. Preserve length and alignment
   information required by its free operation.
5. For collections, reserve before taking interior views, or reacquire views
   after growth. `const` on a slice does not stabilize its backing allocation.

## Choose an arena reset boundary

List every view retained by the next phase, worker, and callback. Transfer the
needed data to longer-lived storage or finish those consumers before reset.
Use a backing allocator that can reclaim pages if per-batch release matters.
Choose retention limits from measured peak memory. Test repeated batches,
including an unusually large one, instead of checking only final deinit.

## Acquire, roll back, transfer

Limit rollback to the scope that owns the resource. If you need the error
value for logging or recovery, catch the result at the caller or in a helper.

For insertion into an owning container, use a helper scope whose successful
exit completes the transfer and disarms rollback. Release resources owned by
individual elements before deinitializing the ArrayList's backing allocation.

For map insertion, define duplicate-key behavior before allocating a replacement.
Free overwritten keys or values explicitly. Test vacant and occupied entries,
plus allocation failure.

## Update transactionally

Allocate and validate the replacement before changing live state. Swap it in,
then free the old value. For a multi-container mutation, either reserve all
fallible capacity before commit or maintain explicit rollback. State which
invariants survive failure. Document partial success if the API permits it.

## Verify

Use `std.testing.allocator` and `std.testing.checkAllAllocationFailures` for
allocating paths. Recreate the same input on each injection run. Check both
cleanup and preservation of old state after a failed update. Test nested-owner
cleanup separately from backing-container cleanup.

Run [ownership.zig](../examples/ownership.zig) for a two-allocation owner,
replacement rollback, nested lists, and an exhausted fixed buffer.
