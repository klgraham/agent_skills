# Zig Error Handling Patterns

## errdefer with Multi-Allocation Loops

When a loop allocates multiple resources sequentially and `errdefer` is active, each allocation must be handled carefully: `errdefer` only cleans up what already exists in the target container. Intermediate allocations between the `try` and the `errdefer` placement can leak.

### Pattern: errdefer after Multiple Allocations in Sequence

```zig
var it = sol.iterator();
while (it.next()) |entry| {
    const key = try allocator.dupe(u8, entry.key_ptr.*);
    var value = entry.value_ptr.clone(allocator) catch {
        // clone() failed (OOM): free the key we just dupe'd.
        // value doesn't exist yet, nothing else in `out` — no further cleanup.
        allocator.free(key);
        return error.OutOfMemory;
    };
    errdefer {
        // Runs if ANY subsequent `try` in this block fails.
        // Cleans up `value` and `key` that are already allocated.
        value.deinit(allocator);
        allocator.free(key);
    }
    try out.put(key, value);
}
```

Key points:
- `var value` (not `const`) because `deinit` takes `*Value`, not `*const Value`
- `catch` block handles OOM from `clone()` — `key` is already allocated, `value` is not yet in `out`
- `errdefer` runs on any failure AFTER the catch block — cleans both `value` and `key`

### Pattern: Manual Cleanup Before Propagation

When `append` can fail after a resource is fully constructed:

```zig
var cloned = try self.cloneSolution(sol);
out.append(self.allocator, cloned) catch {
    self.deinitSolution(&cloned);  // deinit takes *Solution, so `cloned` must be `var`
    return error.OutOfMemory;
};
```

Note: `cloned` must be `var` (not `const`) because `deinitSolution` takes `*Solution`, and `&const_var` is `*const T`.

## Zig 0.16 Breaking Changes

### ArrayList/ArrayListUnmanaged Initializer

Zig 0.16 removed `ArrayList(T){}` struct initialization syntax.

```zig
// Old — does not compile on 0.16
var list = ArrayList(T){};

// Correct — 0.16+
var list = ArrayList(T).empty;
```

Applies to `ArrayList`, `ArrayListUnmanaged`, and `std.ArrayListUnmanaged`.

### GeneralPurposeAllocator Removed

`std.heap.GeneralPurposeAllocator` was removed in Zig 0.16.

```zig
// Old
var gpa = std.heap.GeneralPurposeAllocator(.{}){};
defer _ = gpa.deinit();
const allocator = gpa.allocator();

// Correct — 0.16+
var gpa = std.heap.DebugAllocator(.{}){};
defer _ = gpa.deinit();
const allocator = gpa.allocator();
```

Note: `DebugAllocator` does not leak-check on `deinit()` by default; use `{ .never_unwind = true }` config for leak detection in tests.

### var/const Strictness

Zig 0.16 enforces that variables declared with `var` must be mutated, and `const` must not be. A `var` that is never assigned after initialization is a compile error.

```zig
// Error: local variable is never mutated
var copy = try allocator.dupe(u64, samples);

// Fix: use const
const copy = try allocator.dupe(u64, samples);
```

This also means if you need `*T` (mutable pointer) for a method parameter, the variable must be `var`, not `const`.

### Loop Variable Shadowing Is a Compile Error

In Zig 0.16, naming a loop capture variable the same as an outer scope parameter is a compile error:

```zig
// ERROR: capture 'value' shadows function parameter from outer scope
pub fn writeValueJson(allocator: Allocator, writer: anytype, value: Value) !void {
    // ...
    .vector => |values| {
        for (values, 0..) |value, idx| {  // 'value' shadows function param 'value'
            try writer.print("{e}", .{value});
        }
    },
}
```

Fix: use a different loop variable name:

```zig
.for (values, 0..) |v, idx| {
    try writer.print("{e}", .{v});
}
```

### Threading Allocator Through Writer Functions

When writer functions do internal allocation (e.g., base64 encoding for bytes fields), the allocator must be passed explicitly. Start from the outermost caller and thread through the full chain:

```zig
// Signature change: allocator is FIRST parameter
pub fn writeValueJson(allocator: Allocator, writer: anytype, value: Value) !void

// Caller passes the appropriate allocator
try capi_json.writeValueJson(std.heap.c_allocator, &out.writer, v);  // C API boundary
try jsonl.writeDatomJSONL(db.allocator, w, d);                     // persistent data
try writeDatomJSONL(testing.allocator, w, d);                      // tests
```

After changing any writer signature, grep all callers to find the full call chain:

```bash
grep -rn 'writeValueJson\|writeDatomJson\|writeDatomListJson\|writePullMapJson' src/
```

### std.Io Namespace

The `std.Io` namespace still EXISTS in 0.16 — it was NOT removed. Claims that `std.Io.Writer.Allocating` or `std.Io.Dir.cwd()` need migration are incorrect. Always verify against actual compiler output rather than release notes.
