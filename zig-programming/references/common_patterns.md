# Common Zig Patterns and Idioms

## Error Handling Patterns

### Try-Catch Pattern
```zig
const result = functionThatMayFail() catch |err| {
    // Handle specific error
    return err;
};
```

### Try Shorthand
```zig
const result = try functionThatMayFail();
```

### Error Union with Payload
```zig
fn parseNumber(str: []const u8) !u32 {
    return std.fmt.parseInt(u32, str, 10);
}
```

## Memory Management Patterns

### Allocator Pattern
```zig
const allocator = std.heap.page_allocator;
const items = try allocator.alloc(Item, count);
defer allocator.free(items);
```

### ArenaAllocator for Bulk Freeing
```zig
var arena = std.heap.ArenaAllocator.init(std.heap.page_allocator);
defer arena.deinit();
const allocator = arena.allocator();
// All allocations freed on arena.deinit()
```

### ArrayList Pattern
```zig
var list = std.ArrayList(T).init(allocator);
defer list.deinit();
try list.append(item);
```

## Comptime Patterns

### Generic Functions
```zig
fn max(comptime T: type, a: T, b: T) T {
    return if (a > b) a else b;
}
```

### Comptime Type Introspection
```zig
fn printFieldNames(comptime T: type) void {
    inline for (@typeInfo(T).Struct.fields) |field| {
        std.debug.print("{s}\n", .{field.name});
    }
}
```

### Generic Data Structures
```zig
fn List(comptime T: type) type {
    return struct {
        items: []T,
        len: usize,
    };
}
```

## Optional Patterns

### Optional Unwrapping
```zig
const value = optional_value orelse default_value;
```

### If Optional Payload Capture
```zig
if (optional_value) |value| {
    // Use unwrapped value
} else {
    // Handle null case
}
```

### While with Optionals
```zig
while (iterator.next()) |item| {
    // Process item
}
```

## Union Patterns

### Tagged Union
```zig
const Value = union(enum) {
    int: i32,
    float: f64,
    string: []const u8,
};
```

### Switch on Tagged Union
```zig
switch (value) {
    .int => |i| std.debug.print("int: {}\n", .{i}),
    .float => |f| std.debug.print("float: {}\n", .{f}),
    .string => |s| std.debug.print("string: {s}\n", .{s}),
}
```

## Struct Patterns

### Anonymous Struct Literal
```zig
const point = .{ .x = 10, .y = 20 };
```

### Struct with Methods
```zig
const Point = struct {
    x: i32,
    y: i32,
    
    pub fn init(x: i32, y: i32) Point {
        return .{ .x = x, .y = y };
    }
    
    pub fn distance(self: Point, other: Point) f64 {
        const dx = @as(f64, @floatFromInt(self.x - other.x));
        const dy = @as(f64, @floatFromInt(self.y - other.y));
        return @sqrt(dx * dx + dy * dy);
    }
};
```

## Testing Patterns

### Basic Test
```zig
test "basic test" {
    try std.testing.expect(2 + 2 == 4);
}
```

### Testing with Allocator
```zig
test "with allocator" {
    var arena = std.heap.ArenaAllocator.init(std.testing.allocator);
    defer arena.deinit();
    const allocator = arena.allocator();
    
    const items = try allocator.alloc(u32, 10);
    // Test operations
}
```

## Defer Patterns

### Resource Cleanup
```zig
const file = try std.fs.cwd().openFile("data.txt", .{});
defer file.close();
```

### Error Defer
```zig
const resource = try acquireResource();
errdefer resource.release();
```

## Slicing and Array Patterns

### Slice Creation
```zig
const slice = array[start..end];
const from_start = array[start..];
const to_end = array[0..end];
```

### Sentinel-Terminated Slices
```zig
const str: [:0]const u8 = "null-terminated";
```

## Build Configuration Patterns

### Conditional Compilation
```zig
const is_debug = @import("builtin").mode == .Debug;

if (is_debug) {
    std.debug.print("Debug mode\n", .{});
}
```

### Platform-Specific Code
```zig
const builtin = @import("builtin");

const path_separator = if (builtin.os.tag == .windows) '\\' else '/';
```
