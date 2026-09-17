const std = @import("std");

fn readU32(bytes: []const u8) error{Truncated}!u32 {
    if (bytes.len < 4) return error.Truncated;
    return std.mem.readInt(u32, bytes[0..4], .big);
}

fn section(bytes: []const u8, offset: usize, count: usize, element_size: usize) error{InvalidRange}![]const u8 {
    const length = std.math.mul(usize, count, element_size) catch return error.InvalidRange;
    if (offset > bytes.len or length > bytes.len - offset) return error.InvalidRange;
    return bytes[offset..][0..length];
}

test "binary parsing checks truncation before decoding" {
    const bytes = [_]u8{ 1, 2, 3, 4 };
    for (0..4) |len| try std.testing.expectError(error.Truncated, readU32(bytes[0..len]));
    try std.testing.expectEqual(@as(u32, 0x01020304), try readU32(&bytes));
}

test "section rejects overflow and out of range spans" {
    const bytes = "01234567";
    try std.testing.expectEqualStrings("2345", try section(bytes, 2, 2, 2));
    try std.testing.expectEqualStrings("", try section(bytes, bytes.len, 0, 4));
    try std.testing.expectError(error.InvalidRange, section(bytes, 9, 0, 1));
    try std.testing.expectError(error.InvalidRange, section(bytes, 7, 2, 1));
    try std.testing.expectError(error.InvalidRange, section(bytes, 0, std.math.maxInt(usize), 2));
}
