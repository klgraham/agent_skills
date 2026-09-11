# Comptime and macro alternatives

Use comptime when a type, shape, or validation rule is known during compilation.
Keep decisions from users, files, network data, and runtime CPU probes at runtime.
Zig has no general textual macro preprocessor. Generic functions, returned
container types, reflection, and build-time generators cover different needs.

## Choose the mechanism

| Need | Mechanism | Avoid |
|---|---|---|
| Fixed-size generic container | `fn Buffer(comptime T: type, comptime n: usize) type` returning a struct | Reflection for fields expressible in source |
| Generic operation | A type parameter or a documented `anytype` contract | An implicit ownership contract |
| Per-field serialization or dispatch | `@typeInfo`, `@field`, and `inline for` over comptime fields | Unrolling an ordinary large runtime loop |
| Construct a type from schema data | `@Int`, `@Tuple`, `@Struct`, `@Union`, `@Enum`, `@Pointer`, or `@Fn` as needed | Removed `@Type` recipes |
| Reject an unsupported compile-time parameter | A local `@compileError` with a useful diagnostic | A distant failure inside an unrelated method |
| Large schema, external tool, or inspectable generated source | A generator in the build graph | Doing filesystem I/O during graph configuration |

`@hasDecl` proves that a declaration exists, not that it has the signature or
semantics your generic needs. Instantiate actual calls in tests. Returning a
struct allows methods and ordinary lexical names; use that before constructing
field metadata for `@Struct`.

## Playbook: add a generic

1. Write a concrete instance and identify exactly what varies.
2. Move only those facts to comptime parameters. Document borrowed and owned
   data independently of generic syntax.
3. Reject invalid combinations next to the declaration.
4. Instantiate materially different valid cases. Compile an invalid case and
   check the intended diagnostic.
5. Measure compile time and binary size if specialization creates many copies.
   Reduce generated work before increasing `@setEvalBranchQuota`.

[comptime.zig](../examples/comptime.zig) demonstrates a bounded generic and the
0.16.0 type constructors. [invalid-comptime.zig](../examples/invalid-comptime.zig)
is an intentional compile failure checked by the validation script.

## Playbook: replace a macro

For constants, use named constants. For function-like substitutions, use a
function with explicit argument evaluation. For type-dependent behavior, use
comptime parameters. For token pasting or external schema expansion, generate
source in a host tool and inspect its output. An `inline fn` controls inlining;
it does not turn runtime input into comptime data.

C macro translation is best effort. An untranslatable macro can remain a
compile error until referenced. Test every imported macro you rely on, or put
it behind a small C wrapper. See [C interoperability](c-interop.md).

## Sources

Read [comptime](https://ziglang.org/documentation/0.16.0/#comptime) and the
[builtin reference](https://ziglang.org/documentation/0.16.0/#Builtin-Functions)
for semantics and exact signatures. The
[0.16.0 release notes](https://ziglang.org/download/0.16.0/release-notes.html)
explain the replacement of `@Type`.
