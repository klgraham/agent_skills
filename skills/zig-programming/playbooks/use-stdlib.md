# Zig 0.17.1 runtime APIs

Use for filesystem, HTTP, compression, and container APIs. For backend choice,
stream interfaces, or task design, see [Use std.Io](use-io.md).
Inspect declarations under `std_dir` from `zig env` before adapting a recipe.

Read the [I/O principle](../principles/io.md) for dependency injection.
Bound both the input and the output when decompressing external data.

## API checkpoints

| Task | 0.17.1 form |
|---|---|
| Growable list | `var list: std.ArrayList(T) = .empty` |
| Append and cleanup | `try list.append(gpa, value)` and `list.deinit(gpa)` |
| Read file | `std.Io.Dir.cwd().readFileAlloc(io, path, gpa, .limited(max_bytes))` |
| Write file | `std.Io.Dir.cwd().writeFile(io, .{ .sub_path = path, .data = bytes })` |
| Path manipulation | `std.fs.path.dirname(path)` returns an optional |
| Unbuffered stdout convenience | `std.Io.File.stdout().writeStreamingAll(io, bytes)` |
| HTTP client | `std.http.Client{ .allocator = gpa, .io = io }` |
| Fetch response | `client.fetch(.{ .location = .{ .url = url }, .response_writer = &writer })` |
| Fixed input or output | `std.Io.Reader.fixed(bytes)` or `std.Io.Writer.fixed(buffer)` |
| Gzip | `std.compress.flate.Decompress.init(&reader, .gzip, window)` |
| Big-endian integer | Length check, then `std.mem.readInt(u32, bytes[0..4], .big)` |

`FetchResult` contains status; it is not a response-body owner. The caller's
writer receives the body. A fixed writer bounds output; an allocating writer
alone does not establish a limit. For streaming status checks or a stricter
resource policy, inspect the request-level API before implementing it.

## Playbook: migrate runtime I/O

1. Compile the smallest failing path. Follow the declarations in the pinned
   library instead of guessing names from an older release.
2. Thread `io` from the application boundary through filesystem and network
   calls. Use in-memory readers and writers where no OS operation is needed.
3. Preserve error handling, limits, and ownership while changing signatures.
4. Test empty, truncated, oversized, and malformed data. Include output failure
   and explicit flush handling for buffered writers.
5. Use local fixtures for routine tests. Label external HTTP checks separately.

[runtime.zig](../examples/runtime.zig) runs file, bounded-buffer, and gzip
checks. It also compiles the HTTP path; the verifier does not make a network
request. [binary.zig](../examples/binary.zig) checks lengths and offsets.

## Playbook: migrate ArrayList

Read [the ArrayList migration reference](../references/arraylist-migration.md).
Do not rewrite every anonymous `.{}` initializer: maps and unrelated structs
have different defaults.

## Sources

The [0.16.0 release notes](https://ziglang.org/download/0.16.0/release-notes.html#IO-as-an-Interface)
explain when `std.Io` was introduced. Inspect the installed SDK for current
signatures: `std/Io/Dir.zig`, `std/Io/Reader.zig`, `std/Io/Writer.zig`,
`std/http/Client.zig`, `std/compress/flate/Decompress.zig`, and `std/std.zig`.
