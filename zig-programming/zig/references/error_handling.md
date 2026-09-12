# Error and ownership playbooks

Use `?T` for normal absence, an error union for failure, and a tagged union when
outcomes carry different data. Preserve the original error until an adapter
has a reason to translate it. Do not relabel every error as `OutOfMemory`.

## Acquire, roll back, transfer

Acquire one resource, immediately register its `errdefer`, then acquire the
next. Return the final owner only after all acquisitions succeed. A `defer`
runs on success too; an `errdefer` runs when its scope exits with an error.

The [ownership example](../examples/ownership.zig) tests every allocation
failure in a two-buffer constructor and a replacement operation.

For insertion into an owning container, use a helper scope whose successful
exit completes the transfer. Do not leave an `errdefer` in an outer scope that
can later fail and free the same value a second time. Deinitializing an
ArrayList frees its backing allocation, not resources owned by each element.

For map insertion, define duplicate-key behavior before allocating a replacement.
A map does not automatically free overwritten keys or values. Test both vacant
and occupied entries, plus allocation failure.

## Update transactionally

Allocate and validate the replacement before changing live state. Swap it in,
then free the old value. For a multi-container mutation, either reserve all
fallible capacity before commit or maintain explicit rollback. State which
invariants survive failure; partial success must be a deliberate API contract.

Use `try` to propagate. Use `catch` for recovery or translation. Use
`catch unreachable` only for a locally proved impossibility, never for OOM,
untrusted input, or I/O. Log at the boundary that decides what the failure
means to the user.

## Verify

Use `std.testing.allocator` and `std.testing.checkAllAllocationFailures` for
allocating paths. Recreate the same input on each injection run. Check both
cleanup and preservation of old state after a failed update. Test nested-owner
cleanup separately from backing-container cleanup.

Source: [errors and errdefer](https://ziglang.org/documentation/0.16.0/#Errors),
plus `std/testing.zig` in the pinned compiler.
