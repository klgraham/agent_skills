const std = @import("std");
const c = @cImport({
    @cInclude("helper.h");
});

pub fn answer() c_int {
    return c.answer();
}

test "call crosses the C ABI" {
    try std.testing.expectEqual(@as(c_int, 42), answer());
}
