# Streams and formatting in Zig 0.17.1

Separate the scheduling capability from byte interfaces. `std.Io` supplies OS
operations and concurrency; `std.Io.Reader` and `std.Io.Writer` expose byte
operations. A fixed in-memory reader or writer needs no `Io` argument. File
readers and writers capture the file and `io` when constructed.

## Choose the interface

| Need | Start with |
|---|---|
| In-memory input | `Io.Reader.fixed(bytes)` |
| Bounded in-memory output | `Io.Writer.fixed(buffer)` |
| Growable output | `Io.Writer.Allocating.init(gpa)`; deinit the owner |
| Buffered file output | `file.writer(io, buffer)` and its `.interface` |
| Terminal, pipe, or sequential stream output | `file.writerStreaming(io, buffer)` |
| Sequential file or pipe input | `file.readerStreaming(io, buffer)` and its `.interface` |
| Reusable transformation | Accept `*Io.Reader` and `*Io.Writer` |

Ordinary files and standard streams both use `Io.File` APIs. Do not
combine new stdout examples with old `std.fs.cwd` file recipes.

For implementation steps, see [Read, write, and format streams](../playbooks/process-streams.md).

Primary authority: `std/Io/Reader.zig`, `std/Io/Writer.zig`, and
`std/Io/File.zig`. See [source review](io-sources.md) for the supplied tutorials
and differences checked against this release.
