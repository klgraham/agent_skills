//! Connect a source, a transform, and a sink with bounded queues.

const std = @import("std");
const Io = std.Io;
const testing = std.testing;

const Input = Io.Queue(u16);
const Output = Io.Queue(u32);
const TransferError = Io.Cancelable || Io.QueueClosedError;

fn publish(io: Io, input: []const u16, queue: *Input) TransferError!void {
    defer queue.close(io);
    for (input) |value| try queue.putOne(io, value);
}

fn double(io: Io, input: *Input, output: *Output) TransferError!void {
    defer output.close(io);
    while (true) {
        const value = input.getOne(io) catch |err| switch (err) {
            error.Closed => return,
            error.Canceled => return error.Canceled,
        };
        try output.putOne(io, @as(u32, value) * 2);
    }
}

fn collectSum(io: Io, queue: *Output) (Io.Cancelable || error{Overflow})!u64 {
    var sum: u64 = 0;
    while (true) {
        const value = queue.getOne(io) catch |err| switch (err) {
            error.Closed => return sum,
            error.Canceled => return error.Canceled,
        };
        sum = try std.math.add(u64, sum, value);
    }
}

fn sumDoubled(io: Io, values: []const u16) !u64 {
    var input: Input = .init(&.{});
    var output_buffer: [1]u32 = undefined;
    var output: Output = .init(&output_buffer);

    var transform = try io.concurrent(double, .{ io, &input, &output });
    defer transform.cancel(io) catch {};
    var source = try io.concurrent(publish, .{ io, values, &input });
    defer source.cancel(io) catch {};

    const sum = try collectSum(io, &output);
    try transform.await(io);
    try source.await(io);
    return sum;
}

test "rendezvous pipeline drains its bounded output and handles empty input" {
    try testing.expectEqual(@as(u64, 20), try sumDoubled(testing.io, &.{ 2, 3, 5 }));
    try testing.expectEqual(@as(u64, 0), try sumDoubled(testing.io, &.{}));
}

test "refusal to launch the source joins the waiting transform" {
    var backend: Io.Threaded = .init(testing.allocator, .{ .concurrent_limit = .limited(1) });
    defer backend.deinit();
    try testing.expectError(error.ConcurrencyUnavailable, sumDoubled(backend.io(), &.{42}));
}

test "select over independent receives can consume both inputs" {
    var backend: Io.Threaded = .init_single_threaded;
    const io = backend.io();
    const Queue = Io.Queue(u8);
    var left_buffer: [1]u8 = undefined;
    var right_buffer: [1]u8 = undefined;
    var left: Queue = .init(&left_buffer);
    var right: Queue = .init(&right_buffer);
    try left.putOne(io, 1);
    try right.putOne(io, 2);

    const Result = union(enum) { left: TransferError!u8, right: TransferError!u8 };
    var results: [2]Result = undefined;
    var select: Io.Select(Result) = .init(io, &results);
    defer select.cancelDiscard();
    select.async(.left, Queue.getOne, .{ &left, io });
    select.async(.right, Queue.getOne, .{ &right, io });

    try testing.expectEqual(Result{ .left = 1 }, try select.await());
    try testing.expectEqual(@as(?Result, Result{ .right = 2 }), select.cancel());
}
