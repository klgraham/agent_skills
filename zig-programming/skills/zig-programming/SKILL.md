---
name: zig-programming
description: Expert systems programming assistance for the Zig programming language. Use when writing, debugging, optimizing, or explaining Zig code. Triggers include requests to write Zig programs, debug Zig compilation errors, explain Zig language features (comptime, error handling, memory management), create build.zig files, work with the standard library, optimize Zig code, or convert code from other languages to Zig. Provides idiomatic patterns, build system guidance, and comprehensive language expertise.
---

# Zig Programming

Expert assistance for systems programming with Zig - a general-purpose programming language focused on robustness, optimality, and maintainability.

## Core Principles

When writing Zig code, follow these fundamental principles:

1. **Explicit over implicit**: Make intentions clear through explicit typing and error handling
2. **No hidden control flow**: All control flow is visible in the code
3. **No hidden memory allocations**: Pass allocators explicitly
4. **Compile-time code execution**: Use `comptime` for zero-cost abstractions
5. **Manual memory management**: Use defer for cleanup, pass allocators as parameters

## Quick Start Guide

### Writing a Basic Program

```zig
const std = @import("std");

pub fn main(init: std.process.Init) !void {
    std.debug.print("Hello, {s}!\n", .{"World"});
}
```

### Common Code Patterns

**Error handling with try:**
```zig
const file = try std.fs.cwd().openFile("data.txt", .{});
defer file.close();
```

**Memory allocation:**
```zig
const allocator = std.heap.page_allocator;
const items = try allocator.alloc(u32, 10);
defer allocator.free(items);
```

**Comptime generics:**
```zig
fn max(comptime T: type, a: T, b: T) T {
    return if (a > b) a else b;
}
```

## Language Feature Guide

### Error Handling

Zig uses explicit error handling with error unions (`!`):

```zig
// Function that may fail
fn divide(a: f64, b: f64) !f64 {
    if (b == 0) return error.DivisionByZero;
    return a / b;
}

// Using try to propagate errors
const result = try divide(10, 2);

// Using catch to handle errors
const result = divide(10, 0) catch |err| {
    std.debug.print("Error: {}\n", .{err});
    return;
};

// Using if to check for errors
if (divide(10, 2)) |value| {
    std.debug.print("Success: {}\n", .{value});
} else |err| {
    std.debug.print("Error: {}\n", .{err});
}
```

### Memory Management

Always pass allocators explicitly and use `defer` for cleanup:

```zig
fn processData(allocator: std.mem.Allocator) !void {
    var list = std.ArrayList(i32).init(allocator);
    defer list.deinit();
    
    try list.append(42);
    // list automatically freed on function exit
}
```

**Arena allocator for bulk operations:**
```zig
var arena = std.heap.ArenaAllocator.init(std.heap.page_allocator);
defer arena.deinit();
const allocator = arena.allocator();

// All allocations freed on arena.deinit()
const data1 = try allocator.alloc(u8, 100);
const data2 = try allocator.alloc(u8, 200);
```

### Comptime Programming

Use `comptime` for compile-time code execution:

```zig
// Generic data structures
fn List(comptime T: type) type {
    return struct {
        items: []T,
        len: usize,
        
        pub fn init(allocator: std.mem.Allocator, capacity: usize) !@This() {
            return .{
                .items = try allocator.alloc(T, capacity),
                .len = 0,
            };
        }
    };
}

// Type introspection
fn printFieldNames(comptime T: type) void {
    inline for (@typeInfo(T).Struct.fields) |field| {
        std.debug.print("Field: {s}\n", .{field.name});
    }
}
```

### Optionals

Handle nullable values with `?` and `orelse`:

```zig
const maybe_value: ?i32 = null;

// Provide default value
const value = maybe_value orelse 42;

// Check and unwrap
if (maybe_value) |v| {
    std.debug.print("Value: {}\n", .{v});
} else {
    std.debug.print("No value\n", .{});
}
```

### Structs and Methods

```zig
const Point = struct {
    x: f64,
    y: f64,
    
    pub fn init(x: f64, y: f64) Point {
        return .{ .x = x, .y = y };
    }
    
    pub fn distance(self: Point, other: Point) f64 {
        const dx = self.x - other.x;
        const dy = self.y - other.y;
        return @sqrt(dx * dx + dy * dy);
    }
};

const p1 = Point.init(0, 0);
const p2 = Point{ .x = 3, .y = 4 };
const dist = p1.distance(p2);
```

### Tagged Unions

```zig
const Value = union(enum) {
    int: i64,
    float: f64,
    string: []const u8,
    
    pub fn print(self: Value) void {
        switch (self) {
            .int => |i| std.debug.print("int: {}\n", .{i}),
            .float => |f| std.debug.print("float: {}\n", .{f}),
            .string => |s| std.debug.print("string: {s}\n", .{s}),
        }
    }
};
```

## Build System

### Creating build.zig

Every Zig project needs a `build.zig` file:

```zig
const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const exe = b.addExecutable(.{
        .name = "myapp",
        .root_source_file = b.path("src/main.zig"),
        .target = target,
        .optimize = optimize,
    });

    b.installArtifact(exe);

    const run_cmd = b.addRunArtifact(exe);
    const run_step = b.step("run", "Run the app");
    run_step.dependOn(&run_cmd.step);

    // Add tests
    const tests = b.addTest(.{
        .root_source_file = b.path("src/main.zig"),
        .target = target,
        .optimize = optimize,
    });
    const test_step = b.step("test", "Run tests");
    test_step.dependOn(&b.addRunArtifact(tests).step);
}
```

### Common Build Commands

```bash
zig build              # Build the project
zig build run          # Run the executable
zig build test         # Run tests
zig build -Doptimize=ReleaseFast  # Build optimized
```

For detailed build system patterns, see `references/build_system.md`.

## Testing

Write tests using the `test` keyword:

```zig
const std = @import("std");
const testing = std.testing;

test "basic arithmetic" {
    try testing.expect(2 + 2 == 4);
    try testing.expectEqual(@as(i32, 42), 42);
}

test "with allocator" {
    var arena = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena.deinit();
    const allocator = arena.allocator();
    
    const items = try allocator.alloc(i32, 5);
    try testing.expectEqual(@as(usize, 5), items.len);
}
```

Run with: `zig test src/main.zig`

## Common Tasks

### Creating a New Project

Use the provided script to scaffold a new project:

```bash
python scripts/init_project.py myproject
cd myproject
zig build run
```

### Working with Files

```zig
// Read file
const file = try std.fs.cwd().openFile("data.txt", .{});
defer file.close();
const content = try file.readToEndAlloc(allocator, 1_000_000);
defer allocator.free(content);

// Write file
const out = try std.fs.cwd().createFile("output.txt", .{});
defer out.close();
try out.writeAll("Hello, World!\n");
```

### Working with Strings

```zig
// String formatting
const str = try std.fmt.allocPrint(allocator, "Value: {}", .{42});
defer allocator.free(str);

// Parsing
const num = try std.fmt.parseInt(i32, "123", 10);

// String comparison
const equal = std.mem.eql(u8, str1, str2);

// String splitting
var iter = std.mem.split(u8, "a,b,c", ",");
while (iter.next()) |part| {
    // Process part
}
```

### Working with Collections

```zig
// ArrayList
var list = std.ArrayList(i32).init(allocator);
defer list.deinit();
try list.append(42);

// HashMap
var map = std.StringHashMap(i32).init(allocator);
defer map.deinit();
try map.put("key", 42);
const value = map.get("key");
```

## Debugging Common Errors

### "use of undeclared identifier"
- Ensure the identifier is declared before use
- Check for typos in variable/function names
- Verify imports are correct

### "expected type 'X', found 'Y'"
- Use explicit casts: `@as(TargetType, value)` or `@intCast(value)`
- Check function return types match

### "error: unreachable code"
- Remove code after `return`, `break`, or other control flow
- Check for missing error handling with `try`

### Memory leaks in tests
- Ensure all allocated memory is freed with `defer`
- Use `std.testing.allocator` which detects leaks

## Performance Optimization

1. **Use ReleaseFast mode**: `zig build -Doptimize=ReleaseFast`
2. **Avoid unnecessary allocations**: Reuse buffers, use stack allocation
3. **Use comptime**: Move computations to compile time when possible
4. **Profile first**: Use `zig build -Doptimize=ReleaseFast` with profiling tools
5. **Inline critical functions**: Add `inline` to small, frequently-called functions

## Reference Materials

This skill includes comprehensive reference materials:

- **`references/common_patterns.md`**: Idiomatic Zig patterns for error handling, memory management, comptime programming, testing, and more
- **`references/build_system.md`**: Complete build.zig patterns, cross-compilation, dependencies, and build configurations
- **`references/stdlib_essentials.md`**: Standard library usage guide covering allocators, data structures, I/O, strings, JSON, and testing utilities

Load these references when working on specific aspects of Zig programming.

## Scripts

- **`scripts/init_project.py`**: Scaffold a new Zig project with proper structure, build.zig, and basic setup
