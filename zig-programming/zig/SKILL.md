---
name: zig
description: >
  Route Zig 0.16 work to the focused skills in this collection and provide a
  small set of verified version-specific gotchas. Use when choosing the right
  Zig skill, starting a general Zig task, or checking cross-cutting build,
  stdlib, memory-safety, readability, and data-layout concerns.
license: MIT
metadata:
  hermes:
    tags: [zig, zig-0.16, skill-routing, build-system, stdlib, memory-safety]
    category: software-development
---

# Zig 0.16 Skill Hub

Use this skill as the entrypoint for the Zig skill family. Keep this file
small: route detailed work to one focused sibling instead of duplicating its
workflow. The public repository links below are relative to this directory;
installed skill collections may resolve the same names from their skill root.

## Start every Zig task

1. Read repository instructions, the pinned Zig version, `git status`, public
   declarations, `build.zig` / `build.zig.zon`, and nearby tests.
2. Load [`write-legible-zig`](../write-legible-zig/SKILL.md) before creating,
   modifying, reviewing, or presenting Zig code or Zig guidance.
3. Establish the real verification commands. Run the formatter, focused tests,
   and required build/test target; use direct `zig test` when a build harness
   could be vacuous.
4. Load the focused skill in the routing table before making a specialized
   change. Load more than one when the change crosses boundaries.

## Verified Zig 0.16 checkpoints

These are routing-level reminders, not substitutes for compiling against the
installed compiler:

- Build files use the current Module API (`b.addModule` / `b.createModule`,
  `.root_module`) and `addLibrary(..., .linkage = .static)` where applicable.
- `std.ArrayList(T)` and `std.ArrayListUnmanaged(T)` use `.empty` for an empty
  value in Zig 0.16. Confirm the current managed/unmanaged API in the project
  before copying a container pattern.
- `std.heap.DebugAllocator` replaces the old
  `std.heap.GeneralPurposeAllocator` name in Zig 0.16.
- Zig 0.16 reports an error when a `var` is never mutated. Let the compiler
  identify the exact location and use `const` unless a mutable pointer is part
  of the API contract.
- Run the touched file or test directly with `zig test` when
  `zig build test` might not exercise it.
- Escape literal JSON braces in comptime format strings as `{{` and `}}`.

For version-sensitive stdlib or build claims, inspect the installed compiler
and load the corresponding focused skill rather than extending this list from
memory.

## Cross-cutting ownership checkpoint

Before accepting an allocator, pointer, slice, callback, collection mutation,
or thread-lifecycle change, identify the owner, allocator pairing, borrow
validity interval, invalidators, cleanup path, and synchronization protocol.
Then load [`zig-memory-safety-review`](../zig-memory-safety-review/SKILL.md) for
the ownership ledger, scanner, failure-path exercise, and source-grounded
reporting workflow.

## Routing table

| Need | Focused skill |
|---|---|
| Names, file layout, ownership-visible APIs, error paths, or readable Zig guidance | [`write-legible-zig`](../write-legible-zig/SKILL.md) |
| Ownership, allocator, borrow, invalidation, C ABI, callback, or concurrency audit | [`zig-memory-safety-review`](../zig-memory-safety-review/SKILL.md) |
| SoA, SIMD, cache behavior, arenas, alignment, or bulk processing | [`zig-data-oriented-programming`](../zig-data-oriented-programming/SKILL.md) |
| `build.zig`, `build.zig.zon`, modules, tests, dependencies, or cross-compilation | [`zig-build-system`](../zig-build-system/SKILL.md) |
| Building or installing the Zig compiler | [`zig-build-from-source`](../zig-build-from-source/SKILL.md) |
| Zig 0.16 HTTP, filesystem, compression, binary parsing, or runtime stdlib APIs | [`zig-0.16-stdlib-patterns`](../zig-0.16-stdlib-patterns/SKILL.md) |
| mmap-friendly flat-file storage or zero-copy layouts | [`zig-mmap-project-template`](../zig-mmap-project-template/SKILL.md) |

## Hub references

- [`references/error_handling.md`](references/error_handling.md) — focused
  `errdefer`, allocator pairing, and Zig 0.16 error-handling patterns.
- [`references/updating-zig-skills-for-new-releases.md`](references/updating-zig-skills-for-new-releases.md) — the release-audit process for
  this skill family.
- [`references/zig-skill-tree-design.md`](references/zig-skill-tree-design.md) —
  the lightweight-hub and narrow-sibling design contract.

## Final handoff

Report the focused skill used, the behavior or guidance changed, the exact
formatter/build/test commands run, and any unchecked command or documented
deviation. Keep this hub a router: put new specialized capability in a new
narrow skill rather than growing this file into a second monolith.
