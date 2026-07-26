---
name: zig-0.16-stdlib-patterns
description: "Zig 0.16 stdlib runtime API patterns: HTTP client, file I/O, gzip decompression, binary parsing, and common stdlib API differences from 0.15. Use when writing or debugging Zig code that uses std.http, std.fs, or std.compress."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [zig, stdlib, http, filesystem, zig-0.16]
    category: software-development
    skill_type: reference
---

# Zig 0.16 Stdlib Runtime Patterns

Use when writing or fixing Zig 0.16 source code that uses HTTP, filesystem, or compression APIs.

## HTTP Client — Fetch with body read

```zig
const http = std.http;

var client = http.Client{ .allocator = allocator };
defer client.deinit();

var resp = try client.fetch(allocator, .{
    .location = .{ .url = url },
    .headers = .{
        .user_agent = .{ .override = "Mozilla/5.0" },
    },
});
defer resp.deinit();

if (resp.status != .ok) return error.HttpStatus;
const body = try resp.body().?.readAllAlloc(allocator, max_bytes);
defer allocator.free(body);
```

Key differences from 0.15:
- `client.fetch` takes `(allocator, options)` — not just `(options)`
- `FetchResult` has no `.body` field directly — call `.body()` which returns `?http.Reader`
- Headers use `.override` modifier, not raw string assignment
- `response.deinit()` — response must be deinitialized

## Filesystem — cwd() not top-level

```zig
const fs = std.fs;

// Write file
try fs.cwd().writeFile(path, data);

// Read entire file
const contents = try fs.cwd().readFileAlloc(allocator, path, max_bytes);
defer allocator.free(contents);

// Check existence
fs.cwd().access(path, .{}) catch return false;

// Create directory recursively
fs.cwd().makePath(dir) catch |e| if (e != error.PathAlreadyExists) return e;
```

Key: `fs.cwd()` not `fs.open()` for cwd-relative paths. NOT `os.mkdirParents`, NOT `os.writeFile`, NOT `os.accessat`.

## Path dirname

`fs.dirname(path)` returns `?[]const u8` (optional). No `os.dirname`:

```zig
const cache_dir = fs.dirname(cache_path) orelse return error.NoParentDir;
```

## Gzip Decompression

```zig
const compress = std.compress;

var in_stream = std.io.FixedBufferStream([]const u8){ .buffer = compressed };
var zlib_stream = compress.gzip.GunzipStream{
    .decompressor = compress.gzip.Decompressor.init(allocator, in_stream.reader()),
};
defer zlib_stream.deinit();
const decompressed = try zlib_stream.reader().readAllAlloc(allocator, max_bytes);
```

NOT the `init: {}` anonymous struct builder pattern.

## Big-Endian Binary Parsing (IDX format, etc.)

```zig
fn readBE(comptime T: type, bytes: []const u8) T {
    var result: T = 0;
    for (bytes[0..@sizeOf(T)]) |b| {
        result = (result << 8) | @as(T, b);
    }
    return result;
}
```

Use `@as(T, b)` not `@intCast` or `@IntCast` — the latter don't exist as builtins in 0.16.

## @Vector SIMD Pattern

```zig
var acc: @Vector(8, f32) = @splat(0);
while (i + 8 <= dim) : (i += 8) {
    const va: @Vector(8, f32) = a[i..][0..8].*;
    const vb: @Vector(8, f32) = b[i..][0..8].*;
    acc += (va - vb) * (va - vb);
}
sum += acc[0] + acc[1] + acc[2] + acc[3] + acc[4] + acc[5] + acc[6] + acc[7];
```

## Common Errors

| Error | Fix |
|---|---|
| `root source file 'os' has no member 'mkdirParents'` | Use `fs.cwd().makePath()` |
| `root source file 'os' has no member 'accessat'` | Use `fs.cwd().access(path, .{})` |
| `root source file 'os' has no member 'writeFile'` | Use `fs.cwd().writeFile()` |
| `root source file 'fs' has no member 'cwd'` | `fs` IS the cwd handle — use `fs.cwd()` |
| `root source file 'fs' has no member 'dirname'` | `fs.dirname()` exists but is nullable — use `.orelse` |
| `invalid builtin function: '@IntCast'` | Use `@as(T, value)` for type coercion |
| `unused local constant` in GunzipStream init | Remove the `var s =` wrapper; use direct struct init |
| `fetch` has no parameter called 'user_agent'` | Use `.headers = .{ .user_agent = .{ .override = "..." } }` |
| `fetch` expects 2 arguments | First arg is `allocator`, second is options |
| `FetchResult` has no member 'body'` | Call `.body()` method on response (returns `?http.Reader`) |
| `error: missing struct field: items` on `ArrayListUnmanaged` init | `.{ }` init broken in 0.16 — use `.empty` or explicit `.{ .items = &[_]T{}, .capacity = 0 }`. See `references/zig-0.16-arraylist-migration.md` |
| `std.ArrayListUnmanaged` not found or wrong field count | 0.16 re-exported `ArrayListUnmanaged` as alias for the managed `ArrayList` (with `allocator` field). See `references/zig-0.16-arraylist-migration.md` |
| `std.heap.GeneralPurposeAllocator` not found | Renamed to `std.heap.DebugAllocator(.{}){}` in 0.16 |
| `local variable is never mutated` | 0.16 lint is stricter — change `var` to `const` for any variable that is never written after init |
| `switch must handle all possibilities` on union | 0.16 requires exhaustive switch arms. Add missing union field cases (e.g., new `.vector` variant) |
| `std.Io` namespace removed | **Misdiagnosis** — `std.Io` still exists in 0.16. Check `std.io` vs `std.Io` case; actual fix is usually `ArrayList` init or allocator rename |

### Finding all broken ArrayList initializations

A naive grep for `ArrayList.*{}` misses **anonymous `.{}` initializations** of ArrayList-typed struct fields because the type name isn't on the same line:

```zig
// grep 'ArrayList.*{}' will NOT find this line:
.rows = .{},   // where `rows` is declared as `ArrayList(ArrayList(Value))`
```

**Use the compiler as the ground truth:**
```bash
zig build test 2>&1 | grep "missing struct field: items"
# This catches ALL occurrences, including anonymous `.{}` inits.
```

**After the compiler narrows the file**, read the struct field declarations to confirm the ArrayList type, then fix every `.{}` in that struct's init function (not just the lines matching `ArrayList`).

## Pitfalls

### ArrayListUnmanaged 0.16 Breaking Change

In Zig 0.16, `std.ArrayListUnmanaged` is deprecated and aliased to the **managed** `ArrayList` (which has an `allocator` field alongside `items` and `capacity`). This means:

- `std.ArrayListUnmanaged(T) = std.ArrayList(T)` (identical types)
- The old unmanaged-only struct without allocator no longer exists as a separate type
- Any `.{}` (zero-initialization) of `ArrayListUnmanaged` now fails: `error: missing struct field: items` because the managed version requires `.allocator` too
- The fix is `.empty` (the 0.16 shorthand for zero-initialized managed arrays)

**All of these are broken in 0.16:**

```zig
var list: ArrayListUnmanaged(i32) = .{};              // ERROR
var list: ArrayListUnmanaged(i32) = .{ .items = ..., }; // ERROR (missing capacity, allocator)
```

**Correct in 0.16:**

```zig
var list: ArrayListUnmanaged(i32) = .empty;  // ✓
var list: ArrayListUnmanaged(i32) = .{ .items = &[_]i32{}, .capacity = 0 }; // ✓ (explicit unmanaged style)
```

This applies to ALL `ArrayListUnmanaged` field initializations in structs (e.g., `Graph.init`, `HnswIndex.init`) and local variables in functions.

See `references/zig-0.16-arraylist-migration.md` for full reproduction.

## Reference

- Zig 0.16 stdlib: `/lib/zig/std/http/Client.zig`, `/lib/zig/std/fs.zig`, `/lib/zig/std/compress/gzip.zig`
- ArrayListUnmanaged 0.16 migration: `references/zig-0.16-arraylist-migration.md` (covers `.{ }` → `.empty` fix, type alias chain, complete fix pattern)
- Test APIs: `zig ast-check <file>` for fast compile error checking
