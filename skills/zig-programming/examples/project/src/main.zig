const std = @import("std");
const sample = @import("sample");

pub fn main(init: std.process.Init) !void {
    if (sample.answer() != 42) return error.IncorrectCResult;
    const stdout = std.Io.File.stdout();
    try stdout.writeStreamingAll(init.io, @embedFile("message"));
    const args = try init.minimal.args.toSlice(init.arena.allocator());
    for (args[1..]) |arg| {
        try stdout.writeStreamingAll(init.io, arg);
        try stdout.writeStreamingAll(init.io, "\n");
    }
}
