# Add a generic or replace a macro

Choose a mechanism with the [comptime principle](../principles/comptime.md).

## Add a generic

1. Write a concrete instance and identify exactly what varies.
2. Move only those facts to comptime parameters. Document borrowed and owned
   data independently of generic syntax.
3. Reject invalid combinations next to the declaration.
4. Instantiate materially different valid cases. Compile an invalid case and
   check the intended diagnostic.
5. Measure compile time and binary size if specialization creates many copies.
   Reduce generated work before increasing `@setEvalBranchQuota`.

[comptime.zig](../examples/comptime.zig) demonstrates a bounded generic, type
constructors, and field reflection. [invalid-comptime.zig](../examples/invalid-comptime.zig)
is an intentional compile failure checked by the validation script.

## Replace a macro

For constants, use named constants. For function-like substitutions, use a
function with explicit argument evaluation. For type-dependent behavior, use
comptime parameters. For token pasting or external schema expansion, generate
source in a host tool and inspect its output. An `inline fn` controls
inlining. Pass compile-time data through a `comptime` parameter.

C macro translation is best effort. An untranslatable macro can remain a
compile error until referenced. Test every imported macro you rely on, or put
it behind a small C wrapper. See [C interoperability](integrate-c.md).
