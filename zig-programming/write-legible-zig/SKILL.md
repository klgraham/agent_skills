---
name: write-legible-zig
description: >
  Apply a strict, machine-readable Zig standard when creating, modifying,
  refactoring, debugging, fixing, reviewing, or presenting Zig code. Use for
  .zig files, build.zig and build.zig.zon, Zig APIs, tests, snippets, and
  repository-facing Zig guidance. Triggers: /write-legible-zig, write legible
  Zig, legible Zig, machine-legible Zig, Zig style, Zig conventions, readable
  Zig, or a request to make Zig code easier for agents and humans to change.
  Do not use for general prose questions or non-Zig code unless the request is
  explicitly about a Zig boundary.
---

# Write Legible Zig

Apply the machine-legibility standard to every Zig region created, changed,
reviewed, or presented. Optimize for a reader who must answer one question at
a time: what does this symbol own, which states are possible, where can this
operation fail, and what code must change when the next case is added?

## Load the standard

Read [references/zig-standard.md](references/zig-standard.md) completely before
reasoning about a Zig change. Treat it as the normative implementation and
review checklist.

Use the standard together with repository-local instructions. A repository's
`AGENTS.md`, build contract, public ABI, generated-code boundary, wire format,
and test conventions outrank this skill. When they conflict, preserve the
higher-priority constraint and document the deviation at the code site when it
would otherwise be surprising.

Adapt the standard to Zig; do not transliterate C rules into Zig. Zig's error
unions, `try`, `defer`, `errdefer`, slices, explicit allocators, comptime, and
exhaustive `switch` are part of the legibility surface.

## Work in this order

1. Read applicable user instructions, `AGENTS.md` files, the module imports,
   public declarations, `build.zig` / `build.zig.zon`, and nearby tests.
2. Establish the toolchain and baseline. Read the project-pinned Zig version,
   run `git status`, and identify the build and test commands that actually
   exercise the touched code.
3. Map the touched module's vocabulary: public types, error sets, constants,
   allocators, ownership transfers, borrowed views, state transitions,
   invalidation points, concurrency protocol, and external calls.
4. Preserve behavior and compatibility unless the task requests a semantic
   change. Use an adapter at an incompatible boundary instead of spreading a
   foreign convention through the module.
5. Design names and function boundaries before editing bodies. Classify each
   function as an orchestrator, a leaf, or an adapter; keep one altitude per
   function.
6. Implement the smallest coherent change. Put `defer` and `errdefer` next to
   the acquisition or partial initialization they protect.
7. Run the project's required formatter, build, and tests. Apply the final
   checklist in the reference, then report unchecked commands and justified
   deviations explicitly.

## Choose the matching mode

- **Greenfield module:** use the file-top vocabulary and public-API skeleton in
  section 16 of the standard before filling in behavior.
- **Existing code:** run the near-miss test in section 17. Look for duplicated
  mutation, data encoded as branches, interleaved ownership and computation,
  stale slices, and declarations that live before their first valid value.
  Make the smallest behavior-preserving decomposition that gives the next edit
  a single home.
- **Ownership, allocator, pointer, or concurrency work:** also load
  `zig-memory-safety-review` and prove the lifetime in the source and tests.
- **Build-file work:** also load `zig-build-system`; keep build configuration
  legible without duplicating its canonical templates here.
- **Version-sensitive stdlib work:** also load `zig-0.16-stdlib-patterns` and
  verify the installed compiler rather than relying on remembered APIs.

## Apply the final gate

Before presenting Zig code, re-read the reference checklist. At minimum, run
the repository's formatter and focused tests, then the required build/test
step. When a build harness could be vacuous, run the touched file or test
directly with `zig test`. Use `git diff --check` for the final patch. Never
claim compliance when a required command or rule was not checked.

## Deliver

Report the behavior change, the structural changes that improve legibility, the
verification performed, and any documented deviations. Keep the handoff
shorter than the code review it summarizes.
