const std = @import("std");
const Io = std.Io;

const Job = struct { index: usize, value: i32 };
const Outcome = union(enum) { pending, value: u64, failed: error{NegativeInput} };

fn process(io: Io, value: i32) (Io.Cancelable || error{NegativeInput})!u64 {
    if (value < 0) return error.NegativeInput;
    var sum: u64 = 0;
    for (0..@intCast(value)) |i| {
        if (i % 256 == 0) try io.checkCancel();
        sum += i;
    }
    return sum;
}

fn worker(io: Io, jobs: *Io.Queue(Job), outcomes: []Outcome) Io.Cancelable!void {
    while (true) {
        const job = jobs.getOne(io) catch |err| switch (err) {
            error.Closed => return,
            error.Canceled => return error.Canceled,
        };
        // Each index is enqueued once. No other worker writes this slot.
        const result = process(io, job.value) catch |err| switch (err) {
            error.Canceled => return error.Canceled,
            error.NegativeInput => {
                outcomes[job.index] = .{ .failed = error.NegativeInput };
                continue;
            },
        };
        outcomes[job.index] = .{ .value = result };
    }
}

fn runBatch(io: Io, inputs: []const i32, outcomes: []Outcome) !void {
    if (inputs.len != outcomes.len) return error.LengthMismatch;
    @memset(outcomes, .pending);
    if (inputs.len == 0) return;
    var storage: [2]Job = undefined;
    var jobs: Io.Queue(Job) = .init(&storage);
    var group: Io.Group = .init;
    defer group.cancel(io);
    for (0..3) |_| try group.concurrent(io, worker, .{ io, &jobs, outcomes });
    for (inputs, 0..) |value, index| try jobs.putOne(io, .{ .index = index, .value = value });
    jobs.close(io);
    try group.await(io);
}

test "bounded workers preserve order and record per-job failure" {
    const input = [_]i32{ 5, -1, 10, 0, 3, 4, 8 };
    var outcomes: [input.len]Outcome = undefined;
    try runBatch(std.testing.io, &input, &outcomes);
    const expected = [_]u64{ 10, 0, 45, 0, 3, 6, 28 };
    for (outcomes, expected, 0..) |outcome, value, i| {
        if (i == 1) {
            try std.testing.expectEqual(error.NegativeInput, outcome.failed);
        } else try std.testing.expectEqual(value, outcome.value);
    }
}

test "empty batch works without concurrency and launch refusal leaves no workers" {
    var backend: Io.Threaded = .init_single_threaded;
    const io = backend.io();
    try runBatch(io, &.{}, &.{});
    var outcomes: [1]Outcome = undefined;
    try std.testing.expectError(error.ConcurrencyUnavailable, runBatch(io, &.{1}, &outcomes));
    try std.testing.expect(outcomes[0] == .pending);
}

test "queue close drains buffered elements then rejects puts and gets" {
    const io = std.testing.io;
    var buffer: [2]u32 = undefined;
    var queue: Io.Queue(u32) = .init(&buffer);
    try queue.putOne(io, 7);
    queue.close(io);
    try std.testing.expectEqual(@as(u32, 7), try queue.getOne(io));
    try std.testing.expectError(error.Closed, queue.getOne(io));
    try std.testing.expectError(error.Closed, queue.putOne(io, 8));
}

test "partial worker launch failure cancels the worker already waiting" {
    var backend: Io.Threaded = .init(std.testing.allocator, .{ .concurrent_limit = .limited(1) });
    defer backend.deinit();
    var outcomes: [1]Outcome = undefined;
    try std.testing.expectError(error.ConcurrencyUnavailable, runBatch(backend.io(), &.{1}, &outcomes));
    try std.testing.expect(outcomes[0] == .pending);
}
