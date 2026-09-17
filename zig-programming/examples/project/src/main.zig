const std = @import("std");
const sample = @import("sample");

pub fn main(init: std.process.Init) !void {
    if (sample.answer() != 42) return error.IncorrectCResult;
    try std.Io.File.stdout().writeStreamingAll(init.io, @embedFile("message"));
}
