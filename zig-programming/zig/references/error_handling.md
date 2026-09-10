# Zig Error Handling Patterns

## errdefer after sequential allocations

`errdefer` runs only on the error return path, and only for resources that already exist. Place it immediately after each successful allocation. Allocations between a `try` and its matching `errdefer` can leak.

```zig
const key = try allocator.dupe(u8, source_key);
errdefer allocator.free(key);

var value = try Value.init(allocator, source_value);
errdefer value.deinit(allocator);

try out.put(allocator, key, value);
```

If the second allocation can fail after the first succeeded, free the first resource in that `catch` before propagating. Once both exist, one `errdefer` block can free both until ownership transfers into `out`.

```zig
const key = try allocator.dupe(u8, source_key);
var value = Value.init(allocator, source_value) catch {
    allocator.free(key);
    return error.OutOfMemory;
};
errdefer {
    value.deinit(allocator);
    allocator.free(key);
}
try out.put(allocator, key, value);
```

Use `var` when `deinit` takes `*T`. A `const` binding cannot form that mutable pointer.

## Manual cleanup before transfer

When a later fallible insert can fail after a resource is fully constructed, clean it up in the `catch` before returning. After a successful insert, the container owns the resource.

```zig
var item = try Item.init(allocator, source);
out.append(allocator, item) catch {
    item.deinit(allocator);
    return error.OutOfMemory;
};
```

## Allocator pairing

Free with the same allocator that allocated. Capture it on the owner or thread it through `init`/`deinit`. Do not mix `page_allocator`, `c_allocator`, and a caller-supplied allocator unless the boundary requires it and says so.
