---
name: zig-0-16-stdlib-patterns
description: "Zig 0.16.0 runtime I/O and container migration. Use for std.Io, streams and formatting, async/concurrent tasks, futures, groups, cancellation, select, queues, locks, backend choice, HTTP, and ArrayList migration."
license: MIT
metadata:
  hermes:
    tags: [zig, stdlib, http, filesystem, zig-0.16]
    category: software-development
    skill_type: reference
---

# Zig 0.16.0 runtime APIs

Use for runtime I/O, streams and formatting, task concurrency, parallel work,
and container migration.
Inspect declarations under `std_dir` from `zig env` before adapting a recipe.
This skill targets the release, not earlier 0.16 development snapshots.

## Principles

Pass `std.Io` to runtime operations separately from `std.mem.Allocator`.
Allocation policy and I/O implementation are independent dependencies.
At process startup, `main(init: std.process.Init)` supplies both. In reusable
code, accept only the capabilities the operation needs.

Use bounded reads for external data. A compressed input bound does not bound
decompressed output. Keep interface pointers tied to the reader or writer
object and backing buffers that own their state. Flush buffered output before
reporting success; deferred cleanup cannot propagate a flush error.

## API checkpoints

| Task | 0.16.0 form |
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

[runtime.zig](../zig/examples/runtime.zig) runs file, bounded-buffer, and gzip
checks. It also compiles the HTTP path; the verifier does not make a network
request. [binary.zig](../zig/examples/binary.zig) checks lengths and offsets.

## Playbook: migrate ArrayList

Read [the ArrayList migration reference](references/zig-0.16-arraylist-migration.md).
Do not rewrite every anonymous `.{}` initializer: maps and unrelated structs
have different defaults. `std.ArrayListUnmanaged` is a deprecated alias for
`std.ArrayList`, which does **not** contain an allocator field.

## Choose the std.Io playbook

| Need | Reference |
|---|---|
| Readers, writers, buffers, custom formatting, and streaming records | [Streams and formatting](references/io-streams-formatting.md) |
| async versus concurrent, futures, groups, cancellation, backend selection | [Task concurrency and parallelism](references/io-concurrency.md) |
| Select, deadlines, queues, locks, atomics, raw threads, migration | [Coordination](references/io-coordination.md) |
| Online examples and release-specific corrections | [Source review](references/io-sources.md) |

`io.async` may execute inline. Use `io.concurrent` when progress must overlap,
and handle `ConcurrencyUnavailable`. Neither promises multicore speedup.
Immediately arrange await/cancel cleanup for every task, and keep borrowed
arguments alive until completion. Cancellation requests still require joining.
For bounded pipelines, start consumers before blocking production and close
the queue before normal shutdown. Group completion does not aggregate job errors.

## Sources

Use the [0.16.0 release notes](https://ziglang.org/download/0.16.0/release-notes.html)
for the I/O transition. Exact signatures are in `std/Io/Dir.zig`,
`std/Io/Reader.zig`, `std/Io/Writer.zig`, `std/http/Client.zig`,
`std/compress/flate/Decompress.zig`, and `std/std.zig` in the installed SDK.
