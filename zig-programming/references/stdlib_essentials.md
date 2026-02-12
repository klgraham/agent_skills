# Zig Standard Library Essentials

## Common Imports

```zig
const std = @import("std");
const builtin = @import("builtin");
```

## Memory Allocators

### Common Allocators
```zig
std.heap.page_allocator        // Direct OS allocations
std.heap.GeneralPurposeAllocator  // General use, detects leaks
std.heap.ArenaAllocator        // Bulk free all at once
std.testing.allocator          // For tests, detects leaks
```

### GeneralPurposeAllocator Example
```zig
var gpa = std.heap.GeneralPurposeAllocator(.{}){};
defer _ = gpa.deinit();
const allocator = gpa.allocator();
```

## Data Structures

### ArrayList
```zig
var list = std.ArrayList(i32).init(allocator);
defer list.deinit();

try list.append(42);
try list.appendSlice(&[_]i32{1, 2, 3});
const item = list.pop();
```

### HashMap
```zig
var map = std.StringHashMap(i32).init(allocator);
defer map.deinit();

try map.put("key", 42);
const value = map.get("key");
_ = map.remove("key");
```

### AutoHashMap
```zig
var map = std.AutoHashMap(u32, []const u8).init(allocator);
defer map.deinit();

try map.put(1, "value");
```

### ArrayHashMap (Preserves insertion order)
```zig
var map = std.StringArrayHashMap(i32).init(allocator);
defer map.deinit();
```

## File I/O

### Reading a File
```zig
const file = try std.fs.cwd().openFile("data.txt", .{});
defer file.close();

const content = try file.readToEndAlloc(allocator, 1024 * 1024);
defer allocator.free(content);
```

### Writing a File
```zig
const file = try std.fs.cwd().createFile("output.txt", .{});
defer file.close();

try file.writeAll("Hello, World!\n");
```

### Reading Lines
```zig
const file = try std.fs.cwd().openFile("data.txt", .{});
defer file.close();

var buf_reader = std.io.bufferedReader(file.reader());
var in_stream = buf_reader.reader();

var buf: [1024]u8 = undefined;
while (try in_stream.readUntilDelimiterOrEof(&buf, '\n')) |line| {
    // Process line
}
```

## String Operations

### String Formatting
```zig
const str = try std.fmt.allocPrint(allocator, "Value: {}", .{42});
defer allocator.free(str);
```

### Parsing
```zig
const num = try std.fmt.parseInt(i32, "123", 10);
const float = try std.fmt.parseFloat(f64, "3.14");
```

### String Comparison
```zig
const equal = std.mem.eql(u8, str1, str2);
```

### String Searching
```zig
const index = std.mem.indexOf(u8, haystack, needle);
const last_index = std.mem.lastIndexOf(u8, haystack, needle);
```

### String Splitting
```zig
var iter = std.mem.split(u8, "a,b,c", ",");
while (iter.next()) |part| {
    // Process part
}
```

## Logging

```zig
const log = std.log.scoped(.myapp);

log.debug("Debug message", .{});
log.info("Info: {}", .{value});
log.warn("Warning: {s}", .{message});
log.err("Error: {}", .{error_code});
```

## Time

```zig
const timestamp = std.time.timestamp();
const millis = std.time.milliTimestamp();

std.time.sleep(1 * std.time.ns_per_s); // Sleep 1 second
```

## Random Numbers

```zig
var prng = std.rand.DefaultPrng.init(blk: {
    var seed: u64 = undefined;
    try std.posix.getrandom(std.mem.asBytes(&seed));
    break :blk seed;
});
const rand = prng.random();

const random_int = rand.int(u32);
const random_float = rand.float(f64);
const random_range = rand.intRangeAtMost(u32, 1, 100);
```

## Process and Arguments

```zig
pub fn main(init: std.process.Init) !void {
    var args = try std.process.argsWithAllocator(init.allocator);
    defer args.deinit();
    
    while (args.next()) |arg| {
        std.debug.print("Arg: {s}\n", .{arg});
    }
}
```

### Environment Variables
```zig
const value = std.posix.getenv("PATH");
```

## JSON

### Parsing JSON
```zig
const parsed = try std.json.parseFromSlice(
    MyStruct,
    allocator,
    json_string,
    .{},
);
defer parsed.deinit();

const value = parsed.value;
```

### Writing JSON
```zig
var string = std.ArrayList(u8).init(allocator);
defer string.deinit();

try std.json.stringify(data, .{}, string.writer());
```

## Testing Utilities

```zig
const testing = std.testing;

try testing.expect(condition);
try testing.expectEqual(expected, actual);
try testing.expectError(error.MyError, result);
try testing.expectEqualStrings("expected", actual);
try testing.expectEqualSlices(T, expected, actual);
```

## Debug Utilities

```zig
std.debug.print("Value: {}\n", .{value});
std.debug.print("Pointer: {*}\n", .{&value});
std.debug.print("Type: {s}\n", .{@typeName(@TypeOf(value))});
```

## Math Operations

```zig
const max_val = @max(a, b);
const min_val = @min(a, b);
const abs_val = @abs(value);
const sqrt_val = @sqrt(value);
const pow_val = std.math.pow(f64, base, exponent);
```
