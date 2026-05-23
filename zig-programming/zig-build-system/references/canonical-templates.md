# Canonical 0.16 Templates

These are the exact files produced by `zig init` (as of Zig 0.16.0) with light annotations.

## build.zig.zon

```zig
.{
    .name = .example,
    .version = "0.0.0",
    .fingerprint = 0xa9c13febcb836352, // Changing this has security implications
    .minimum_zig_version = "0.16.0",
    .dependencies = .{},
    .paths = .{
        "build.zig",
        "build.zig.zon",
        "src",
    },
}
```

## build.zig (full)

See the main `SKILL.md` for the annotated version. The raw output from `zig init` is the best source of truth — run it when you need the absolute latest.

## src/main.zig (juicy main example)

```zig
const std = @import("std");
const Io = std.Io;

const example = @import("example");

pub fn main(init: std.process.Init) !void {
    const arena = init.arena.allocator();
    const args = try init.minimal.args.toSlice(arena);

    const io = init.io;

    var stdout_buffer: [1024]u8 = undefined;
    var stdout_writer: Io.File.Writer = .init(.stdout(), io, &stdout_buffer);
    const stdout = &stdout_writer.interface;

    try example.printMessage(stdout);
}
```

## src/root.zig

```zig
const std = @import("std");

pub fn printMessage(writer: anytype) !void {
    try writer.print("Hello from the library\n", .{});
}
```

**Tip**: Always start a new project with `zig init` rather than copying old templates. The structure above is the current recommendation.
