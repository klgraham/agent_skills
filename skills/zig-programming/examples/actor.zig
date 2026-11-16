//! Serialize updates to a task-owned peak and reply to a snapshot request.

const std = @import("std");
const Io = std.Io;
const testing = std.testing;

const Reply = Io.Queue(?u32);
const Command = union(enum) {
    observe: u32,
    snapshot: *Reply,
};
const Mailbox = Io.Queue(Command);

fn serve(io: Io, mailbox: *Mailbox) Io.Cancelable!void {
    var peak: ?u32 = null;
    while (true) {
        const command = mailbox.getOne(io) catch |err| switch (err) {
            error.Closed => return,
            error.Canceled => return error.Canceled,
        };
        switch (command) {
            .observe => |value| peak = @max(peak orelse value, value),
            .snapshot => |reply| reply.putOne(io, peak) catch |err| switch (err) {
                error.Closed => {},
                error.Canceled => return error.Canceled,
            },
        }
    }
}

fn snapshotAfterObservations(io: Io, observations: []const u32) !?u32 {
    var mailbox_buffer: [2]Command = undefined;
    var mailbox: Mailbox = .init(&mailbox_buffer);
    // There is one snapshot request. Its reply fits even while the caller joins.
    var reply_buffer: [1]?u32 = undefined;
    var reply: Reply = .init(&reply_buffer);
    var actor = try io.concurrent(serve, .{ io, &mailbox });
    defer actor.cancel(io) catch {};

    for (observations) |value| try mailbox.putOne(io, .{ .observe = value });
    try mailbox.putOne(io, .{ .snapshot = &reply });
    mailbox.close(io);
    try actor.await(io);
    reply.close(io);
    return reply.getOne(io);
}

test "actor drains commands in order and keeps its reply available after join" {
    try testing.expectEqual(@as(?u32, 8), try snapshotAfterObservations(testing.io, &.{ 1, 8, 3 }));
    try testing.expectEqual(@as(?u32, null), try snapshotAfterObservations(testing.io, &.{}));
}

test "launch refusal is returned before any command is sent" {
    var backend: Io.Threaded = .init_single_threaded;
    try testing.expectError(error.ConcurrencyUnavailable, snapshotAfterObservations(backend.io(), &.{42}));
}
