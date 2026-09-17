---
name: zig-programming
description: Develop, review, optimize, migrate, and package Zig software with version-grounded guidance. Use for Zig source, build.zig, stdlib and std.Io APIs, ownership and memory safety, C interoperability, comptime, data layout and SIMD, mmap formats, compiler builds, and Zig release migrations. This collection targets Zig 0.16.0 unless the project pins another version.
---

# Zig programming

Route Zig work to the smallest relevant playbook. Verify disputed language and library behavior against the project-pinned compiler rather than remembered APIs.

## Route the task

Choose one primary playbook by the user's intent. Read that playbook, its required principles, and only the conditional references that apply. Do not preload the library.

| Intent | Playbook |
|---|---|
| General Zig source work not dominated by a focused intent below | [Write legible Zig](playbooks/write-legible-zig.md) |
| Configure modules, dependencies, generated files, tests, cross-compilation, or releases | [Build a Zig project](playbooks/build-project.md) |
| Use or migrate runtime I/O, streams, formatting, containers, HTTP, or concurrency | [Use Zig 0.16 stdlib](playbooks/use-stdlib.md) |
| Audit ownership, borrowing, invalidation, cleanup, callbacks, or shared state | [Review memory safety](playbooks/review-memory-safety.md) |
| Optimize measured hot paths, layout, allocation, SIMD, or parallel work | [Optimize data layout](playbooks/optimize-data-layout.md) |
| Design a binary format, mapped snapshot, or mmap-backed data structure | [Design mmap storage](playbooks/design-mmap-storage.md) |
| Bootstrap or install the Zig compiler from source | [Build the compiler](playbooks/build-compiler.md) |
| Move this skill collection to another Zig release | [Update the Zig release](playbooks/update-zig-release.md) |

For a compound request, start with the playbook that establishes the missing contract. Apply the legibility playbook to every Zig code change, but do not turn ordinary allocation work into a repository-wide memory-safety audit. Build-file work and version-sensitive stdlib work use their focused playbooks alongside legibility.

## Establish the contract

Read repository instructions, the compiler pin, `build.zig`, `build.zig.zon`, public APIs, and nearby tests. Run `zig version` and `zig env` when a compiler is available. This collection targets **Zig 0.16.0**, not an arbitrary development snapshot or a later release. Do not upgrade a project merely because this skill targets a different version.

For language rules, consult the [0.16.0 language reference](https://ziglang.org/documentation/0.16.0/). For library signatures, inspect the `std_dir` reported by that compiler. Use the [0.16.0 release notes](https://ziglang.org/download/0.16.0/release-notes.html) to distinguish actual changes from older idioms. Compile disputed examples.

## Select principles by mechanism

The selected playbook names its required resources. Add a principle when the mechanism warrants it; do not load all principles by default.

| Mechanism or question | Principle |
|---|---|
| Storage lifetime, bounds, allocator ownership, arenas, or allocation failure | [Allocators](principles/allocators.md) |
| Error sets, rollback, ownership transfer, or transactional mutation | [Error handling](principles/error-handling.md) |
| Headers, ABI layout, foreign allocation, callbacks, or exported APIs | [C interoperability](principles/c-interop.md) |
| Generics, reflection, type construction, compile-time validation, or macro replacement | [Comptime](principles/comptime.md) |

## Use bundled resources only when needed

- Code legibility: [Zig standard](references/zig-standard.md).
- Stream and formatting details: [streams and formatting](references/io-streams-formatting.md).
- Futures, groups, cancellation, and backend choice: [task concurrency](references/io-concurrency.md).
- Select, queues, locks, atomics, and raw threads: [coordination](references/io-coordination.md).
- Release-specific online examples and corrections: [I/O sources](references/io-sources.md).
- `ArrayList` migration: [ArrayList migration](references/zig-0.16-arraylist-migration.md).
- Layered graph formats: [graph layout](references/graph-layout.md).
- Executable contracts: [examples](examples/) and `scripts/verify_examples.py`.
- Heuristic ownership inventory: `scripts/zig_memory_safety_scan.py`; verify every candidate in source.

Resolve all resource and script paths relative to this skill directory.

## Verify and deliver

Run the repository formatter and focused tests, then the build step that actually reaches the changed code. Use direct `zig test` when the build graph could be vacuous. Add allocation-failure, malformed-input, invalidation, shutdown, or boundary cases when those contracts change. Distinguish native execution from cross-compilation and compile success from runtime, performance, or memory-safety evidence.

Report the behavior changed, commands executed, results observed, and coverage limits. Do not claim a speedup without measurements or safety from compilation alone.

For maintenance of this collection, run `python3 scripts/verify_examples.py` from this directory with Zig 0.16.0, plus `python3 scripts/test_zig_memory_safety_scan.py` when the scanner or its packaging changes.
