---
name: zig
description: "Zig 0.16.0 principles and playbooks for implementation, migration, allocators, C interoperability, comptime, builds, runtime I/O, and verification. Use for general Zig work or to select a focused Zig skill."
license: MIT
metadata:
  hermes:
    tags: [zig, zig-0.16, skill-routing, build-system, stdlib, memory-safety]
    category: software-development
---

# Zig 0.16.0

Use this hub for Zig implementation, design, migration, and review. Read only
the principles and playbooks relevant to the task. The sibling skill names
remain usable when installed together under a different skill root.

## Establish the contract

Read repository instructions, the compiler pin, build files, public APIs, and
nearby tests. Run `zig version` and `zig env`. This collection targets **0.16.0**,
not an arbitrary 0.16 development snapshot or a later release. Do not upgrade a
project merely because this skill targets a different version.

For language rules, consult the [0.16.0 reference](https://ziglang.org/documentation/0.16.0/).
For library signatures, inspect the `std_dir` reported by that compiler.
Use the [release notes](https://ziglang.org/download/0.16.0/release-notes.html)
to distinguish actual changes from older Zig idioms. Compile disputed examples.

## Principles and their playbooks

| Decision | Read when needed |
|---|---|
| Choose storage by lifetime, bound, and allocator ownership | [Allocator principles and playbooks](references/allocators.md) |
| Keep failure paths transactional and transfer ownership once | [Error handling](references/error_handling.md) |
| Turn foreign representations into checked Zig contracts | [C interoperability](references/c-interop.md) |
| Specialize compile-time facts without hiding runtime policy | [Comptime and macro alternatives](references/comptime.md) |
| Make dependencies, generated files, and releases explicit | [Build system](../zig-build-system/SKILL.md) |
| Streams, formatting, task concurrency, and parallel work through `std.Io` | [Runtime stdlib](../zig-0-16-stdlib-patterns/SKILL.md) |
| Prove borrow validity across mutation and shutdown | [Memory-safety review](../zig-memory-safety-review/SKILL.md) |
| Measure layout and SIMD choices against a scalar baseline | [Data-oriented programming](../zig-data-oriented-programming/SKILL.md) |
| Validate a byte format before exposing mapped views | [mmap storage](../zig-mmap-project-template/SKILL.md) |
| Keep names, state, and cleanup readable | [Write legible Zig](../write-legible-zig/SKILL.md) |
| Build the compiler itself with matched dependencies | [Build from source](../zig-build-from-source/SKILL.md) |

For code changes, apply the legibility standard alongside the relevant
playbook. Ordinary allocation does not require a repository-wide safety audit.
Use the audit when the task concerns lifetimes, shared state, or unsafe boundaries.

## 0.16.0 checkpoints

- `std.ArrayList(T)` does not store an allocator. Initialize with `.empty`,
  and pass the same allocator to allocating methods and `deinit`.
- Runtime filesystem operations use `std.Io.Dir` and an `std.Io` value.
  `main(init: std.process.Init)` supplies `init.io` and `init.gpa`.
- `@Type` is removed. Type construction uses dedicated builtins such as
  `@Int`, `@Tuple`, and `@Struct`. Prefer ordinary type syntax when sufficient.
- `@intCast` exists. `@as` is not a replacement for a checked narrowing cast.
- Build artifacts take `.root_module`. A test compile step does not run tests.

## Verification and handoff

Run the project's formatter and focused tests. Check that the build's test
step reaches the changed code. Add allocation-failure or boundary cases when
those contracts change. Distinguish native execution from cross-compilation.
Report the outcome, commands, and limitations without claiming performance
or memory safety from compilation alone.

For maintenance of this collection, run
`python3 zig/scripts/verify_examples.py` from `zig-programming/`.
It requires Zig 0.16.0 and checks the [runnable examples](examples/).
Use the [release-update playbook](references/updating-zig-skills-for-new-releases.md)
when revising the version baseline.
