const std = @import("std");
const Io = std.Io;

// gzip.compress(b"gzip fixture", mtime=0), stored as bytes to keep the fixture reviewable.
const gzip_fixture = [_]u8{
    0x1f, 0x8b, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02, 0xff, 0x4b, 0xaf, 0xca, 0x2c, 0x50, 0x48, 0xcb, 0xac, 0x28, 0x29, 0x2d, 0x4a, 0x05, 0x00, 0x36, 0x58, 0x3c, 0x87, 0x0c, 0x00, 0x00, 0x00,
};

fn fetchBounded(io: Io, gpa: std.mem.Allocator, url: []const u8) !void {
    var client: std.http.Client = .{ .allocator = gpa, .io = io };
    defer client.deinit();
    var bytes: [4096]u8 = undefined;
    var output = Io.Writer.fixed(&bytes);
    const result = try client.fetch(.{
        .location = .{ .url = url },
        .response_writer = &output,
    });
    if (result.status != .ok) return error.HttpStatus;
    try Io.File.stdout().writeStreamingAll(io, output.buffered());
}

pub fn main(init: std.process.Init) !void {
    const io = init.io;
    const gpa = init.gpa;
    const args = try init.minimal.args.toSlice(init.arena.allocator());
    // The verifier never supplies a URL. This branch still checks HTTP codegen.
    if (args.len == 2) return fetchBounded(io, gpa, args[1]);

    const cwd = Io.Dir.cwd();
    const filename = "runtime-fixture.txt";
    try cwd.writeFile(io, .{ .sub_path = filename, .data = "runtime fixture" });
    defer cwd.deleteFile(io, filename) catch {};
    const read = try cwd.readFileAlloc(io, filename, gpa, .limited(100));
    defer gpa.free(read);
    try std.testing.expectEqualStrings("runtime fixture", read);
    try std.testing.expectError(error.StreamTooLong, cwd.readFileAlloc(io, filename, gpa, .limited(3)));

    var input = Io.Reader.fixed(&gzip_fixture);
    var window: [std.compress.flate.max_window_len]u8 = undefined;
    var decompress = std.compress.flate.Decompress.init(&input, .gzip, &window);
    const decoded = try decompress.reader.allocRemaining(gpa, .limited(100));
    defer gpa.free(decoded);
    try std.testing.expectEqualStrings("gzip fixture", decoded);

    var short_input = Io.Reader.fixed(&gzip_fixture);
    var short_window: [std.compress.flate.max_window_len]u8 = undefined;
    var limited = std.compress.flate.Decompress.init(&short_input, .gzip, &short_window);
    try std.testing.expectError(error.StreamTooLong, limited.reader.allocRemaining(gpa, .limited(3)));
    var output_bytes: [2]u8 = undefined;
    var output = Io.Writer.fixed(&output_bytes);
    try std.testing.expectError(error.WriteFailed, output.writeAll("too long"));
    try Io.File.stdout().writeStreamingAll(io, "runtime checks passed\n");
}
