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

`@hasDecl` sees only public declarations in 0.17. It does not check signatures.
Instantiate actual calls in tests. For structs and unions, `@typeInfo` exposes
parallel `field_names` and `field_types` arrays. Iterate both with `inline for`
instead of using the old `.fields` array. Prefer returning an ordinary struct
when you do not need to construct field metadata with `@Struct`.

See [Add a generic or replace a macro](../playbooks/use-comptime.md) for implementation steps.

## Sources

Read [comptime](https://ziglang.org/documentation/0.17.1/#comptime) and the
[builtin reference](https://ziglang.org/documentation/0.17.1/#Builtin-Functions)
for semantics and signatures. The [0.17.0 release notes](https://ziglang.org/download/0.17.0/release-notes.html)
explain the changes to `@hasDecl` and `std.lang.Type`.
