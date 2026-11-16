# ArrayList in Zig 0.17.1

`std.ArrayList(T)` is `std.array_list.Aligned(T, null)`. Pass an allocator to
allocating operations and cleanup. `std.ArrayListUnmanaged` is a deprecated alias
for the same type; the separate legacy managed forms in `std.array_list` store
the allocator.

```zig
const std = @import("std");

test "list lifetime" {
    const gpa = std.testing.allocator;
    var values: std.ArrayList(u32) = .empty;
    defer values.deinit(gpa);
    try values.append(gpa, 42);
    try std.testing.expectEqual(@as(u32, 42), values.items[0]);
}
```

## Migration procedure

1. Identify the actual field type from its declaration, including aliases.
2. For an empty ArrayList, use `.empty`. `.{}` omits required fields.
3. Supply the same allocator for allocating operations and cleanup.
4. For nested owners, free each child before the outer list. `pop()` returns
   an optional element; transfer its cleanup responsibility explicitly.
5. Reacquire `.items` views after growth. Use `toOwnedSlice(gpa)` only when
   transferring the allocation, and free the resulting slice with that allocator.
6. Compile every caller and run allocation-failure tests. Anonymous initializers
   can be missed by searches for the word `ArrayList`.

Do not bulk-convert map initialization or change `var` based only on text
matching. Do not serialize the container object: slices contain process-local
pointers. Serialize element data using an explicit format.

Use `last()` for an optional last value and `lastPtr()` for an optional borrowed
pointer. In safety-enabled builds, `lockPointers()` paired with `unlockPointers()`
can catch list operations that would invalidate a live item pointer. It does not
synchronize threads, track a copied list, or replace a lifetime argument.

Run [ownership.zig](../examples/ownership.zig) for nested cleanup and
allocation failure coverage. Inspect `std/std.zig` and `std/array_list.zig`
from `zig env` for the alias and method definitions.
