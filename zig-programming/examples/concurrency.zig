const std = @import("std");
const Io = std.Io;
const testing = std.testing;

fn double(x: u32) u32 {
    return x * 2;
}

test "inline async works and required concurrency can be unavailable" {
    var backend: Io.Threaded = .init_single_threaded;
    const io = backend.io();
    var task = io.async(double, .{21});
    try testing.expectEqual(@as(u32, 42), task.await(io));
    try testing.expectError(error.ConcurrencyUnavailable, io.concurrent(double, .{21}));
}

fn waitForCancellation(io: Io, ready: *Io.Event, finished: *bool) Io.Cancelable!void {
    defer finished.* = true;
    ready.set(io);
    while (true) try io.checkCancel();
}

test "cancel joins a CPU task and runs its deferred cleanup" {
    const io = testing.io;
    var ready: Io.Event = .unset;
    var finished = false;
    var task = try io.concurrent(waitForCancellation, .{ io, &ready, &finished });
    defer task.cancel(io) catch {};
    try ready.wait(io);
    try testing.expectError(error.Canceled, task.cancel(io));
    // Cancellation completion, not the ready signal, synchronizes this read.
    try testing.expect(finished);
}

fn fail() error{JobFailed}!void {
    return error.JobFailed;
}

fn earlyFailure(io: Io, finished: *bool) !void {
    var ready: Io.Event = .unset;
    var sibling = try io.concurrent(waitForCancellation, .{ io, &ready, finished });
    defer sibling.cancel(io) catch {};
    try ready.wait(io);
    var failing = io.async(fail, .{});
    defer failing.cancel(io) catch {};
    try failing.await(io);
}

test "task failure cannot abandon a sibling borrowing local data" {
    var finished = false;
    try testing.expectError(error.JobFailed, earlyFailure(testing.io, &finished));
    try testing.expect(finished);
}

fn allocate(gpa: std.mem.Allocator) ![]u8 {
    return gpa.dupe(u8, "owned");
}

test "cancel may return a completed owned result which needs freeing" {
    var backend: Io.Threaded = .init_single_threaded;
    const io = backend.io();
    var task = io.async(allocate, .{testing.allocator});
    const abandoned_result = try task.cancel(io);
    defer testing.allocator.free(abandoned_result);
    try testing.expectEqualStrings("owned", abandoned_result);
}

fn deadline(io: Io) Io.Cancelable!void {
    try io.sleep(.fromMilliseconds(1), .awake);
}

fn waitForever(io: Io, finished: *bool) Io.Cancelable!u32 {
    defer finished.* = true;
    var event: Io.Event = .unset;
    try event.wait(io);
    unreachable;
}

test "select deadline cancels and joins the blocked loser" {
    const io = testing.io;
    const Outcome = union(enum) { work: Io.Cancelable!u32, timeout: Io.Cancelable!void };
    var buffer: [2]Outcome = undefined;
    var select: Io.Select(Outcome) = .init(io, &buffer);
    var finished = false;
    defer select.cancelDiscard();
    try select.concurrent(.work, waitForever, .{ io, &finished });
    try select.concurrent(.timeout, deadline, .{io});
    switch (try select.await()) {
        .timeout => |result| try result,
        .work => return error.UnexpectedWinner,
    }
    select.cancelDiscard();
    try testing.expect(finished);
}

test "select cancellation drains owning results" {
    var backend: Io.Threaded = .init_single_threaded;
    const io = backend.io();
    const Outcome = union(enum) { bytes: std.mem.Allocator.Error![]u8 };
    var buffer: [2]Outcome = undefined;
    var select: Io.Select(Outcome) = .init(io, &buffer);
    defer while (select.cancel()) |result| {
        switch (result) {
            .bytes => |bytes| if (bytes) |owned| testing.allocator.free(owned) else |_| {},
        }
    };
    select.async(.bytes, allocate, .{testing.allocator});
    select.async(.bytes, allocate, .{testing.allocator});
}

const Shared = struct {
    mutex: Io.Mutex = .init,
    condition: Io.Condition = .init,
    ready: bool = false,
    value: u32 = 0,
};

fn publish(io: Io, shared: *Shared) Io.Cancelable!void {
    try shared.mutex.lock(io);
    defer shared.mutex.unlock(io);
    shared.value = 42;
    shared.ready = true;
    shared.condition.signal(io);
}

test "condition waits on a predicate protected by the same mutex" {
    const io = testing.io;
    var shared: Shared = .{};
    var task = try io.concurrent(publish, .{ io, &shared });
    defer task.cancel(io) catch {};
    {
        try shared.mutex.lock(io);
        defer shared.mutex.unlock(io);
        while (!shared.ready) try shared.condition.wait(io, &shared.mutex);
        try testing.expectEqual(@as(u32, 42), shared.value);
    }
    try task.await(io);
}

fn count(counter: *std.atomic.Value(u32)) void {
    for (0..1000) |_| _ = counter.fetchAdd(1, .monotonic);
}

test "group completion precedes reading an independent atomic counter" {
    const io = testing.io;
    var counter: std.atomic.Value(u32) = .init(0);
    var group: Io.Group = .init;
    defer group.cancel(io);
    for (0..3) |_| try group.concurrent(io, count, .{&counter});
    try group.await(io);
    try testing.expectEqual(@as(u32, 3000), counter.load(.monotonic));
}

fn threadResult(result: *u32) void {
    result.* = 42;
}

test "raw thread result storage remains alive through join" {
    var result: u32 = 0;
    {
        const thread = try std.Thread.spawn(.{}, threadResult, .{&result});
        defer thread.join();
    }
    try testing.expectEqual(@as(u32, 42), result);
}

fn holdPermit(io: Io, sem: *Io.Semaphore, ready: *Io.Event) Io.Cancelable!void {
    try sem.wait(io);
    defer sem.post(io);
    ready.set(io);
    var never: Io.Event = .unset;
    try never.wait(io);
}

test "canceling a permit holder restores the semaphore" {
    const io = testing.io;
    var sem: Io.Semaphore = .{ .permits = 1 };
    var ready: Io.Event = .unset;
    var task = try io.concurrent(holdPermit, .{ io, &sem, &ready });
    defer task.cancel(io) catch {};
    try ready.wait(io);
    try testing.expectError(error.Canceled, task.cancel(io));
    try sem.wait(io);
    sem.post(io);
}
