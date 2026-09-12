const std = @import("std");
const Io = std.Io;

const Progress = struct {
    done: u32,
    total: u32,

    pub fn format(self: Progress, out: *Io.Writer) Io.Writer.Error!void {
        try out.print("{d}/{d}", .{ self.done, self.total });
    }
};

fn report(out: *Io.Writer, progress: Progress) Io.Writer.Error!void {
    try out.print("progress={f} {{ok}}\n", .{progress});
}

test "custom formatter works with a bounded writer and propagates full output" {
    var buffer: [64]u8 = undefined;
    var out = Io.Writer.fixed(&buffer);
    try report(&out, .{ .done = 2, .total = 3 });
    try std.testing.expectEqualStrings("progress=2/3 {ok}\n", out.buffered());
    var small: [1]u8 = undefined;
    var short = Io.Writer.fixed(&small);
    try std.testing.expectError(error.WriteFailed, report(&short, .{ .done = 2, .total = 3 }));
}

test "buffered file writer flushes before its output is read" {
    const io = std.testing.io;
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();
    const file = try tmp.dir.createFile(io, "report.txt", .{});
    defer file.close(io);
    var buffer: [64]u8 = undefined;
    var writer = file.writer(io, &buffer);
    try report(&writer.interface, .{ .done = 2, .total = 3 });
    try writer.interface.flush();
    const bytes = try tmp.dir.readFileAlloc(io, "report.txt", std.testing.allocator, .limited(100));
    defer std.testing.allocator.free(bytes);
    try std.testing.expectEqualStrings("progress=2/3 {ok}\n", bytes);
}

test "line input preserves empty records and an unterminated final record" {
    var input = Io.Reader.fixed("one\n\nlast");
    try std.testing.expectEqualStrings("one", (try input.takeDelimiter('\n')).?);
    try std.testing.expectEqualStrings("", (try input.takeDelimiter('\n')).?);
    try std.testing.expectEqualStrings("last", (try input.takeDelimiter('\n')).?);
    try std.testing.expectEqual(@as(?[]u8, null), try input.takeDelimiter('\n'));
}

test "small file reader streams lines and rejects an overlong record" {
    const io = std.testing.io;
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();
    try tmp.dir.writeFile(io, .{ .sub_path = "lines", .data = "a\nb\n123456789" });
    const file = try tmp.dir.openFile(io, "lines", .{});
    defer file.close(io);
    var buffer: [4]u8 = undefined;
    var reader = file.readerStreaming(io, &buffer);
    try std.testing.expectEqualStrings("a", (try reader.interface.takeDelimiter('\n')).?);
    try std.testing.expectEqualStrings("b", (try reader.interface.takeDelimiter('\n')).?);
    try std.testing.expectError(error.StreamTooLong, reader.interface.takeDelimiter('\n'));
}
