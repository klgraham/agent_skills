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

## Playbook: call a C library

1. Translate its actual header in one module. For a small ABI you control, a
   matching `extern fn` declaration may suffice. Configure include paths, C
   sources, and libraries in `build.zig`. Set `.link_libc = true` when the module
   needs libc; a declaration does not link its implementation.
2. Identify which results borrow, transfer ownership, or require a release call.
3. Translate failure at the adapter. Check conversion ranges and any required
   alignment before a pointer cast.
4. Test a real call across the boundary. Merely referencing a translated type
   does not verify linkage or parameter passing.
5. For each supported target, compile with that target's dependencies. Execute
   ABI tests on supported native systems or a declared emulator.

The [example project](../examples/project/build.zig) compiles a C helper against
its local header and calls it through one `extern fn`. In a copy of that
directory, run `zig build test` and `zig build run` to exercise the call.

## Playbook: expose Zig to C

Write the public header first. Prefer opaque handles with paired create/destroy
functions. Specify whether a null pointer is allowed for a zero-length buffer,
who owns outputs, and whether the caller may invoke functions concurrently.
Return stable status values instead of Zig errors. Add a C caller that links
the built library and exercises success, invalid inputs, and cleanup. Assert
sizes and offsets on both sides when sharing record layouts.

Do not rely on panic recovery across C frames. Handle recoverable failures
before returning through the ABI. For C++ libraries, use a C wrapper unless a
project-specific binding already defines a tested C++ ABI contract.

## Sources

[C interoperability](https://ziglang.org/documentation/0.17.1/#C) covers
translation and ABI rules. Inspect `std/Build/Module.zig` for
`addCSourceFile`, `addIncludePath`, and `linkSystemLibrary` in the pinned SDK.
