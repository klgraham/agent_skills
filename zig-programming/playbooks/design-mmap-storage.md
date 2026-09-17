# mmap storage in Zig 0.16.0

Use for flat-file storage and mapped snapshots. Separate mutable construction
from the validated read-only format. Mapping a file is an I/O implementation
choice; it does not establish the safety or portability of its bytes.

## Principles

Store fixed-width integers, explicit endianness, offsets, lengths, and a format
version. Do not persist pointers, slices, allocator handles, ArrayList objects,
or native struct padding. `extern struct` describes a target's C ABI, not a
portable serialization format.

A mapping owner controls every borrowed view. Unmapping, replacement, file
truncation, and concurrent writes can invalidate readers. Keep a published
snapshot immutable or define a synchronization and reclamation protocol.

## Playbook: define a format

1. Specify the magic, version, byte order, header size, reserved bytes, and each
   section's element size and alignment. Define malformed-file errors.
2. Validate the header length before reading it. Decode integers from bytes.
3. Check multiplication and integer conversions before computing a section size.
4. Check `offset <= file_len`, then `length <= file_len - offset` before slicing.
   Validate IDs, counts, cross-section relationships, and required alignment.
5. Use byte decoding when alignment or representation is not guaranteed.
   `@alignCast` checks an assumption; it does not repair an unaligned address.
6. Expose borrowed views only after validation and tie their validity to the owner.

[binary.zig](../examples/binary.zig) gives runnable length and range checks.
For layered graph data, load [graph layouts](../references/graph-layout.md), which
covers public IDs, dense indices, layer identity, and compacted-state checks.

## Playbook: implement mapping and persistence

Isolate platform mapping and unmapping in one owner. Inspect the pinned SDK's
platform API rather than copying an old `std.os.mmap` call. Define behavior for
empty files and failures after mapping. Register unmapping cleanup before
parsing can fail. Closing the file descriptor and unmapping are distinct events;
follow the platform contract.

Encode a snapshot into a temporary file, check writes and flush or sync errors,
and publish it using the platform's replacement contract. If crash durability
is required, specify file and directory synchronization; a rename alone is not
a complete durability argument. Keep old mappings alive until their readers
finish. Do not mutate or truncate a mapped snapshot behind those readers.

## Project setup and verification

Use the [build playbook](build-project.md) for modules, manifests,
and test roots. Creating a local library does not imply creating a remote repo.
For runtime reads and writes use the [std.Io playbook](use-stdlib.md).

Test round trips, truncation at every header boundary, oversized counts,
overflowing ranges, invalid versions, misalignment, and stale snapshot state.
For mapped implementations, also test owner shutdown and replacement with live
readers under the intended synchronization contract. Fuzz the byte parser
independently of mapping. Do not dereference an invalid borrow to test that a
safe API rejects it.

Use [memory-safety review](review-memory-safety.md) for mapping
lifetimes, callbacks, and concurrent reclamation. Source rules for pointers and
alignment are in the [0.16.0 reference](https://ziglang.org/documentation/0.16.0/).
