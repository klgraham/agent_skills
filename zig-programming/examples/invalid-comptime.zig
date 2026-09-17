const Buffer = @import("comptime.zig").Buffer;
comptime {
    _ = Buffer(u8, 0);
}
