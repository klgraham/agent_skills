# Read, write, and format streams

Choose an interface from [streams and formatting](../references/io-streams-formatting.md).

## Write and format

1. Construct the writer owner and buffer in the scope that uses them. Keep an
   interface pointer tied to that owner. Moving the owner can invalidate it.
2. Use a literal format string with typed arguments. Use `{s}` for text,
   `{d}` for decimal values, `{x}` for hex, and `{f}` for a custom formatter.
   Escape literal braces as `{{` and `}}`.
3. Define custom formatting as `format(self, writer: *Io.Writer) Io.Writer.Error!void`.
   Propagate writer errors. Keep formatters free of hidden allocation or I/O
   beyond the supplied writer unless the API explicitly requires it.
4. Explicitly `try writer.interface.flush()` before returning success from
   buffered file output and before closing the file.
5. Release allocating writers after copying or transferring any needed output.
   Their buffered view is borrowed and may be invalidated by later writes.

Use `std.mem.print(buffer, format, args)` for a one-shot format into caller
storage or `gpa.print(format, args)` for owned output. Free the owned result
with the same allocator. These replace older `std.fmt.bufPrint` and
`std.fmt.allocPrint` recipes.

Use the format-specific encoder to quote JSON strings or escape HTML. Validate
UTF-8 wherever the data contract requires it.
Handle underlying file-reader/writer diagnostics when generic `ReadFailed` or
`WriteFailed` is insufficient. Inspect the owner's error fields in the pinned SDK.

## Process a bounded stream

Use a reusable transform taking reader/writer interfaces. Choose whether the
limit applies per record, per request, or to total output, and enforce it there.
Count bytes across reads when the limit applies to total input. `stream` can
return partial progress. Use `streamExact` when the protocol specifies a byte
count. Use `streamRemaining` when reading to EOF is appropriate.

For line input, `takeDelimiter` returns an optional borrowed slice and can
report `StreamTooLong`. Consume or copy each slice before advancing the reader.
Define behavior for an unterminated final line. Test fragmented input, empty
records, EOF, an overlong record, and output failure.

When a stream hands records to concurrent workers, copy into owned messages
or retain stable immutable backing storage. An ordinary reader buffer view can
be overwritten on the next read.

[streams.zig](../examples/streams.zig) exercises buffered file formatting,
a custom formatter, line EOF behavior, and bounded output failure. The existing
[runtime example](../examples/runtime.zig) adds gzip and file-size limits.
