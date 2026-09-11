const std = @import("std");

pub fn Buffer(comptime T: type, comptime capacity: usize) type {
    if (capacity == 0) @compileError("Buffer capacity must be positive");
    return struct {
        items: [capacity]T = undefined,
        len: usize = 0,

        pub fn append(self: *@This(), value: T) error{Full}!void {
            if (self.len == capacity) return error.Full;
            self.items[self.len] = value;
            self.len += 1;
        }
    };
}

test "generic capacity and element types" {
    var integers: Buffer(u16, 2) = .{};
    try integers.append(4);
    try integers.append(9);
    try std.testing.expectError(error.Full, integers.append(10));
    var flags: Buffer(bool, 1) = .{};
    try flags.append(true);
    try std.testing.expect(flags.items[0]);
}

test "0.16 type constructors and field reflection" {
    const Small = @Int(.unsigned, 10);
    const Pair = @Tuple(&.{ Small, bool });
    const pair: Pair = .{ 1023, true };
    try std.testing.expectEqual(@as(Small, 1023), pair[0]);
    const Record = @Struct(.auto, null, &.{"value"}, &.{u32}, &.{.{}});
    const record: Record = .{ .value = 7 };
    inline for (@typeInfo(Record).@"struct".fields) |field| {
        try std.testing.expectEqual(@as(u32, 7), @field(record, field.name));
    }
}
