const std = @import("std");
const c = struct {
    // Mirrors the single declaration in include/helper.h.
    extern fn answer() c_int;
};

pub fn answer() c_int {
    return c.answer();
}

test "call crosses the C ABI" {
    try std.testing.expectEqual(@as(c_int, 42), answer());
}
