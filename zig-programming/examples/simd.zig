const std = @import("std");

fn dot(comptime width: usize, a: []const f32, b: []const f32) error{LengthMismatch}!f32 {
    if (width == 0) @compileError("vector width must be positive");
    if (a.len != b.len) return error.LengthMismatch;
    var i: usize = 0;
    var lanes: @Vector(width, f32) = @splat(0);
    while (a.len - i >= width) : (i += width) {
        const av: @Vector(width, f32) = a[i..][0..width].*;
        const bv: @Vector(width, f32) = b[i..][0..width].*;
        lanes += av * bv;
    }
    var sum: f32 = @reduce(.Add, lanes);
    while (i < a.len) : (i += 1) sum += a[i] * b[i];
    return sum;
}

fn scalarDot(a: []const f32, b: []const f32) f32 {
    var sum: f32 = 0;
    for (a, b) |x, y| sum += x * y;
    return sum;
}

test "SIMD agrees with scalar around vector boundaries" {
    var a: [19]f32 = undefined;
    var b: [19]f32 = undefined;
    for (&a, &b, 0..) |*x, *y, i| {
        x.* = @as(f32, @floatFromInt(i)) * 0.25 - 2;
        y.* = @as(f32, @floatFromInt(i % 5)) * 0.5;
    }
    inline for (.{ 4, 8 }) |width| {
        for (0..a.len + 1) |len| {
            try std.testing.expectApproxEqAbs(scalarDot(a[0..len], b[0..len]), try dot(width, a[0..len], b[0..len]), 0.0001);
        }
    }
    try std.testing.expectError(error.LengthMismatch, dot(4, a[0..2], b[0..1]));
}

test "lane selection has an explicit element type" {
    const values: @Vector(4, f32) = .{ -1, 2, -3, 4 };
    const zero: @Vector(4, f32) = @splat(0);
    const positive = @select(f32, values > zero, values, zero);
    try std.testing.expectEqual(@as(f32, 6), @reduce(.Add, positive));
}
