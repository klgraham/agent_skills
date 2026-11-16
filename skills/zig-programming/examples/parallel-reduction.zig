//! Count matching bytes in two independently executable chunks.

const std = @import("std");
const Io = std.Io;
const testing = std.testing;

const cancellation_check_interval = 1024;

fn countChunk(io: Io, bytes: []const u8, needle: u8) Io.Cancelable!usize {
    var count: usize = 0;
    for (bytes, 0..) |byte, index| {
        if (index % cancellation_check_interval == 0) try io.checkCancel();
        if (byte == needle) count += 1;
    }
    return count;
}

fn countMatches(io: Io, bytes: []const u8, needle: u8) Io.Cancelable!usize {
    const midpoint = bytes.len / 2;
    var first = io.async(countChunk, .{ io, bytes[0..midpoint], needle });
    errdefer _ = first.cancel(io) catch 0;

    const second_count = try countChunk(io, bytes[midpoint..], needle);
    const first_count = try first.await(io);
    return first_count + second_count;
}

test "chunked count matches the sequential result on both configurations" {
    var inline_backend: Io.Threaded = .init_single_threaded;
    const input = "ababaadea";
    const expected = try countChunk(testing.io, input, 'a');
    for ([_]Io{ testing.io, inline_backend.io() }) |io| {
        try testing.expectEqual(expected, try countMatches(io, input, 'a'));
        try testing.expectEqual(@as(usize, 0), try countMatches(io, "", 'a'));
    }
}
