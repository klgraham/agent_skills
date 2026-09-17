# Streams and formatting in Zig 0.16.0

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

Ordinary files and standard streams both use the 0.16.0 `Io.File` APIs. Do not
combine new stdout examples with old `std.fs.cwd` file recipes.

## Playbook: write and format

1. Construct the writer owner and buffer in the scope that uses them. Keep an
   interface pointer tied to that owner; moving the owner can invalidate it.
2. Use a literal format string with typed arguments. Use `{s}` for text,
   `{d}` for decimal values, `{x}` for hex, and `{f}` for a custom formatter.
   Escape literal braces as `{{` and `}}`.
3. Define custom formatting as `format(self, writer: *Io.Writer) Io.Writer.Error!void`.
   Propagate writer errors. Keep formatters free of hidden allocation or I/O
   beyond the supplied writer unless the API explicitly requires it.
4. Explicitly `try writer.interface.flush()` before returning success from
   buffered file output. Closing the file does not flush your user-space writer.
5. Release allocating writers after copying or transferring any needed output.
   Their buffered view is borrowed and may be invalidated by later writes.

Formatting is not serialization escaping. `{s}` does not quote JSON strings,
escape HTML, or validate UTF-8. Use the format-specific encoder at that boundary.
Handle underlying file-reader/writer diagnostics when generic `ReadFailed` or
`WriteFailed` is insufficient; inspect the owner's error fields in the pinned SDK.

## Playbook: process a bounded stream

Use a reusable transform taking reader/writer interfaces. Choose whether the
limit applies per record, per request, or to total output, and enforce it there.
A small reader buffer alone does not bound total input. `stream` can return
partial progress; use `streamExact` when exactly N bytes form the protocol unit,
or `streamRemaining` only when reading to EOF is appropriate.

For line input, `takeDelimiter` returns an optional borrowed slice and can
report `StreamTooLong`. Consume or copy each slice before advancing the reader.
Define behavior for an unterminated final line. Test fragmented input, empty
records, EOF, an overlong record, and output failure.

When a stream hands records to concurrent workers, copy into owned messages
or retain stable immutable backing storage. Reader buffer views cannot outlive
the next read merely because a queue is thread-safe.

[streams.zig](../examples/streams.zig) exercises buffered file formatting,
a custom formatter, line EOF behavior, and bounded output failure. The existing
[runtime example](../examples/runtime.zig) adds gzip and file-size limits.

Primary authority: `std/Io/Reader.zig`, `std/Io/Writer.zig`, and
`std/Io/File.zig`. See [source review](io-sources.md) for the supplied tutorials
and differences checked against this release.
