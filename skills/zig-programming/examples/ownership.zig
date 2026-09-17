const std = @import("std");
const Allocator = std.mem.Allocator;

const Document = struct {
    allocator: Allocator,
    name: []u8,
    body: []u8,

    fn init(gpa: Allocator, name: []const u8, body: []const u8) !Document {
        const owned_name = try gpa.dupe(u8, name);
        errdefer gpa.free(owned_name);
        const owned_body = try gpa.dupe(u8, body);
        return .{ .allocator = gpa, .name = owned_name, .body = owned_body };
    }

    fn deinit(self: *Document) void {
        self.allocator.free(self.body);
        self.allocator.free(self.name);
    }

    fn replaceBody(self: *Document, input: []const u8) !void {
        const replacement = try self.allocator.dupe(u8, input);
        const old = self.body;
        self.body = replacement;
        self.allocator.free(old);
    }
};

fn exerciseOwner(gpa: Allocator) !void {
    var doc = try Document.init(gpa, "title", "old body");
    defer doc.deinit();
    doc.replaceBody("new body") catch |err| {
        try std.testing.expectEqualStrings("old body", doc.body);
        return err;
    };
    try std.testing.expectEqualStrings("new body", doc.body);
}

fn appendOwned(gpa: Allocator, lists: *std.ArrayList(std.ArrayList(u8))) !void {
    var inner: std.ArrayList(u8) = .empty;
    errdefer inner.deinit(gpa);
    try inner.appendSlice(gpa, "owned");
    try lists.append(gpa, inner);
    // Successful return ends temporary ownership. The outer owner cleans up.
}

fn exerciseNested(gpa: Allocator) !void {
    var lists: std.ArrayList(std.ArrayList(u8)) = .empty;
    defer {
        for (lists.items) |*inner| inner.deinit(gpa);
        lists.deinit(gpa);
    }
    try appendOwned(gpa, &lists);
    try appendOwned(gpa, &lists);
    try std.testing.expectEqualStrings("owned", lists.items[1].items);
}

test "owner initialization and replacement survive every allocation failure" {
    try std.testing.checkAllAllocationFailures(std.testing.allocator, exerciseOwner, .{});
}

test "nested list transfers have exactly one cleanup authority" {
    try std.testing.checkAllAllocationFailures(std.testing.allocator, exerciseNested, .{});
}

test "fixed buffer exhaustion is an ordinary error" {
    var bytes: [8]u8 = undefined;
    var fba = std.heap.FixedBufferAllocator.init(&bytes);
    const gpa = fba.allocator();
    _ = try gpa.alloc(u8, 8);
    try std.testing.expectError(error.OutOfMemory, gpa.alloc(u8, 1));
}
