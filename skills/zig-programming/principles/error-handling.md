# Error handling and rollback

Use `?T` for normal absence, an error union for failure, and a tagged union when
outcomes carry different data. Preserve the original error until an adapter
has a reason to translate it. Do not relabel every error as `OutOfMemory`.

Use `try` to propagate. Use `catch` for recovery or translation. Use
`catch unreachable` only for a locally proved impossibility, never for OOM,
untrusted input, or I/O. Log at the boundary that decides what the failure
means to the user.

## Rollback invariants

An error must leave each live resource with one owner and each exposed
invariant intact. Define partial success in the API when the caller needs
to distinguish committed work from work that can be retried.

A `defer` runs on success as well as failure. An `errdefer` runs when its
scope exits with an error. Zig 0.17 removed the `errdefer |err|` capture.

See [Manage allocation](../playbooks/manage-allocation.md) for acquisition,
ownership transfer, and transactional updates.

Source: [errors and errdefer](https://ziglang.org/documentation/0.17.1/#Errors),
plus `std/testing.zig` in the pinned compiler.
