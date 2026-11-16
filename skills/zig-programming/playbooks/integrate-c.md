# Integrate Zig and C

Review the [C interoperability principle](../principles/c-interop.md) for
ABI and ownership contracts.

## Call a C library

1. Translate its actual header in one module. For a small ABI you control, a
   matching `extern fn` declaration may suffice. Configure include paths, C
   sources, and libraries in `build.zig`. Link each implementation you call.
   Set `.link_libc = true` when the module needs libc.
2. Identify which results borrow, transfer ownership, or require a release call.
3. Translate failure at the adapter. Check conversion ranges and any required
   alignment before a pointer cast.
4. Test a real call across the boundary to verify linkage and parameter passing.
5. For each supported target, compile with that target's dependencies. Execute
   ABI tests on supported native systems or a declared emulator.

The [example project](../examples/project/build.zig) compiles a C helper against
its local header and calls it through one `extern fn`. In a copy of that
directory, run `zig build test` and `zig build run` to exercise the call.

## Expose Zig to C

Write the public header first. Prefer opaque handles with paired create/destroy
functions. Specify whether a null pointer is allowed for a zero-length buffer,
who owns outputs, and whether the caller may invoke functions concurrently.
Return stable status values instead of Zig errors. Add a C caller that links
the built library and exercises success, invalid inputs, and cleanup. Assert
sizes and offsets on both sides when sharing record layouts.

Handle recoverable failures before control crosses the C boundary. For C++
libraries, use a C wrapper unless a project-specific binding already defines
a tested C++ ABI contract.
