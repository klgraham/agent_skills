# C interoperability

Keep ABI details in a small adapter. Convert C status codes, pointer-length
pairs, and allocation rules into the Zig module's error and ownership contract.
A successful cast or header import does not prove the foreign object is valid.

## Principles

- Zig 0.17 removed `@cImport`, `@cInclude`, and related builtins. To generate
  bindings in `build.zig`, use the [official `translate-c` package migration](https://ziglang.org/download/0.17.0/release-notes.html#C-Translation-Moving-to-External-Package)
  and import the translator's module with `@import("c")` (or the module name
  declared in the build). `b.addTranslateC` is deprecated. Use `zig translate-c`
  for one-off inspection.
- Match translation and compilation target, include paths, defines, ABI, and
  compiler flags. Host headers are not automatically valid for another target.
- Use C-compatible integers and `extern struct` for ABI records. `packed struct`
  is not a general replacement for C layout or C bitfields.
- Keep slices, error unions, and Zig-owned containers inside Zig. Export an
  explicit pointer, length, status, and destroy contract across a C boundary.
- A sentinel pointer promises a terminator. An ordinary slice does not.
  Check nullability and length before constructing a slice from C memory.
- Match the allocator and its matching release function. Never assume a foreign
  `destroy` is interchangeable with `free`, even when both eventually use libc.
- Make callbacks `callconv(.c)` where the header requires the C calling
  convention. Keep context alive until unregister and in-flight calls finish.

See [Integrate Zig and C](../playbooks/integrate-c.md) for import, export, and linkage procedures.

## Sources

[C interoperability](https://ziglang.org/documentation/0.17.1/#C) covers
translation and ABI rules. Inspect `std/Build/Module.zig` for
`addCSourceFile`, `addIncludePath`, and `linkSystemLibrary` in the pinned SDK.
