---
name: zig
description: Zig 0.16 software development workflows — project setup, building from source, stdlib API patterns, and mmap-friendly library design. Use when writing, debugging, or building Zig projects.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [zig, build-system, stdlib, http, filesystem, mmap, zig-0.16]
    category: software-development
---

# Zig 0.16 Development

All Zig work targets version 0.16. Key changes from 0.15:
- `addStaticLibrary` → `addLibrary` with `.linkage = .static`
- `b.addModule` replaces module composition in constructors
- `standardOptimizeOption(.{})` replaces `standardOptimizeOption(mode)`
- `std.http.Client.fetch` now takes `(allocator, options)`
- `std.fs` — use `fs.cwd()` for current-directory-relative paths
- `@IntCast` → `@as(T, value)`
- **`std.ArrayListUnmanaged` / `std.ArrayList` initialization**: In Zig 0.16, `ArrayListUnmanaged(T){}` (empty struct literal) fails with `missing struct field: items`. Use `ArrayListUnmanaged(T).empty` instead. Same for `std.ArrayList(T).empty`. This also applies to type aliases like `const ArrayList = std.ArrayListUnmanaged;` — use `ArrayList(T).empty` or `SolutionSet.empty` where `SolutionSet = ArrayList(Solution)`.
  - **Fix**: global search/replace `= ArrayList\(.*?\)\{\}` with `= ArrayList($1).empty` across the codebase.
  - Applies to: `graph.zig`, `index.zig`, `layer.zig`, database/query code, tests, and any Zig 0.16 code.
- **`std.Io` namespace**: `std.Io` APIs (`Writer.Allocating`, `Dir.cwd()`, `Limit.limited`) still exist in Zig 0.16 stable. However, `std.ArrayList(u8).init(allocator)` + `.writer()` is the more idiomatic and stable pattern for allocating writers. If a codebase was using `std.Io.Writer.Allocating`, it likely still compiles — but prefer `ArrayList` + `writer()` for new code.
  - **Fix in capi.zig / serialization**: Replace `var out = std.Io.Writer.Allocating.init(allocator);` with `var list = std.ArrayList(u8).init(allocator); defer list.deinit(); var out = list.writer();`. The writer interface remains compatible with `writer.print()` etc.
- **`std.heap.GeneralPurposeAllocator` → `std.heap.DebugAllocator`**: In Zig 0.16 stable, `GeneralPurposeAllocator` was renamed to `DebugAllocator`. Any test or bench script using `var gpa = std.heap.GeneralPurposeAllocator(.{}){};` must become `var gpa = std.heap.DebugAllocator(.{}){};`. This is a hard compilation error, not a deprecation warning.
  - **Fix**: `rg "GeneralPurposeAllocator"` across the repo, replace all occurrences.
- **Stricter `var` / `const` lint**: Zig 0.16 now errors on `var x = ...` when `x` is never mutated after initialization. The error message is explicit: `local variable is never mutated` / `consider using 'const'`. This affects test files, bench scripts, and any code where `var` was used defensively.
  - **Fix**: compile, let Zig tell you which variables, change `var` → `const`. There is no bulk autofix — Zig's error messages give exact line numbers.
- **`std.fmt` comptime format string strictness**: `std.fmt` treats `{` and `}` as format delimiters. When building JSON with `std.fmt.bufPrint`/`print`, every literal JSON brace must be escaped as `{{` or `}}`. A string like `"{\"a\":{d}}"` fails at comptime; use `"{{\"a\":{d}}}"`. This affects any comptime-known format strings containing JSON or `{`/`}` literals.
- **Priority queue / BFS inversion bug**: Using `sort(ascending)` + `pop()` removes the **farthest** element, not nearest. Sort **descending** when `pop()` is the intended nearest-first dequeue. Affects BFS layer search, nearest-neighbor expansion, Dijkstra-style graph traversal.
  - **Zig pattern**: `std.mem.sort(T, items, {}, struct { fn less(...) bool { return a.distance > b.distance; } }.less)` — descending so `pop()` returns nearest.
  - **Real bug caught in zig-hnsw**: `layer.zig:findKNearest` sorted `<` (ascending) then `pop()` — BFS was expanding farthest node instead of nearest. Fixed by inverting comparator.
- **`zig test <file>` vs `zig build test`**: When the build system is broken, `zig build test` can produce empty output with exit 0 (harness passes but tests don't run). Always directly test individual files: `zig test src/hnsw_test.zig` to actually exercise the tests.
- **`@floatFromInt` needs explicit result type in switch prongs**: When using `@floatFromInt(i)` inside a `switch` expression whose result feeds into `@floatCast()`, each prong must independently have a known type. Use `@as(f64, @floatFromInt(i))`. The outer `@floatCast` only provides the target type after the switch evaluates, not inside its prongs. Also applies when assigning: `@floatCast(switch (item) { .integer => |i| @as(f64, @floatFromInt(i)), ... })`.\n- **@constCast for allocator-safe mutations**: When a method takes `*Self` solely for allocator access (not to mutate state), use `@constCast` with a safety comment. Example: `const hnsw_mut = @constCast(&self.hnsw);` before calling a search method through a const `self`. Safe when the method only allocates temporary results. Document the reason in a comment.\n- **Test allocator leak prevention**: `testing.allocator.dupe(f32, &[_]f32{...})` leaks heap memory in debug builds. For comptime-known data, use comptime array slices: `&[_]f32{ 1.0, 0.0, 0.0 }` — static memory, no deallocation needed. Only use `allocator.dupe()` for runtime data with guaranteed cleanup.\n- **Unused local constant**: Zig 0.16 does NOT suppress warnings with `_` prefix on locals (unlike function parameters). If extracting a value only for type validation: `_ = switch (args[1]) { .constant => |v| switch (v) { .integer => {}, else => return error.X }, else => return error.X };` — validate via switch, discard result.\n- **Pointless discard with defer**: Zig 0.16 flags `_ = x;` as pointless discard when `x` is used later by a `defer`. Don't discard variables that have deferred cleanup — they ARE used. If a test body is empty, convert to a doc-only test.
- **`@floatFromInt` needs explicit result type in switch prongs**: When a `switch` expression feeds into `@floatCast()`, each prong must produce a known type. `@floatFromInt(i)` without context fails — use `@as(f64, @floatFromInt(i))`. Same when assigning to a `f32` via `@floatCast(switch (...) { .integer => |i| @as(f64, @floatFromInt(i)), ... })`. The outer `@floatCast(f64→f32)` provides the target only after the switch evaluates, not inside it.
- **Test allocator leak prevention**: `testing.allocator.dupe(f32, &[_]f32{...})` leaks heap memory in debug builds. For comptime-known data, use comptime array slices: `&[_]f32{ 1.0, 0.0, 0.0 }` — static memory, no deallocation needed. Only use `allocator.dupe()` for runtime data with guaranteed cleanup.
- **@constCast for allocator-safe mutations**: When a method takes `*Self` only for allocator access (not to mutate state), use `@constCast` with a safety comment. Example: `const hnsw_mut = @constCast(&self.hnsw);` before calling search through a const `self`. Safe when the method only allocates.
- **Unused local constant**: Zig 0.16 does not suppress warnings with `_` prefix on locals. If extracting a value only for type validation, validate via switch without binding, then discard the switch result: `_ = switch (args[1]) { .constant => |v| switch (v) { .integer => {}, else => return error.X }, else => return error.X }`.

## Memory Audit Workflow

When reviewing a Zig codebase for memory safety (e.g., before open-sourcing or deploying as a managed service), follow this systematic audit:

1. **Map allocator usage**
   - Search for all allocator sources: `gpa`, `c_allocator`, `page_allocator`, `testing.allocator`, `ArenaAllocator`.
   - Identify which allocators own persistent vs. temporary data. Persistent structures should use a passed-in or GPA; temporary work should use arena or stack.

2. **Verify `defer` / `errdefer` pairing**
   - Every `create`/`alloc`/`dupe`/`clone` needs a matching `defer free`/`destroy`/`deinit` on the success path.
   - Every fallible allocation inside a function that returns an error needs `errdefer` cleanup.
   - Watch for error-path leaks: if `A = alloc(); B = alloc(); return {A, B};` and B's alloc fails, A leaks unless guarded by `errdefer`.

3. **Check arena lifecycle**
   - `ArenaAllocator.init(allocator)` must be paired with `defer arena.deinit()`.
   - If an arena backs a long-lived object (e.g., `Database`), ensure `arena.reset(.{ .retain_capacity = {} })` is called periodically, or document why it grows unbounded.

4. **Run debug builds with leak detection**
   - `zig build test -Doptimize=Debug`
   - `zig test src/foo.zig` directly (not through the build harness) when the build system might silently skip tests.
   - The `testing.allocator` in debug mode will crash with a leak trace if any test leaves memory unfreed.

5. **Audit C ABI boundaries**
   - Exported functions returning caller-owned memory must document the free function (e.g., `ss_bytes_free`).
   - Global error strings (`g_last_error`) should be freed on replacement and on library teardown, or use a static buffer.
   - `c_allocator` allocations inside exported functions need `errdefer` to avoid leaking on error returns.

6. **Common leak patterns to flag**
   - `page_allocator` used for small, frequent buffers (bypasses leak detection and wastes pages).
   - `std.fmt.allocPrint` / `std.heap.c_allocator.dupe` without corresponding free.
   - `cloneSolution`-style functions that allocate temporaries before inserting into a container: if the container append fails, the temporaries leak unless covered by `errdefer`.
   - `ArrayList(T).empty` initialized lists that are never `deinit`ed.

---

## Design Philosophy: Data-Oriented Zig

Zig's design independently converges on **data-oriented programming** principles. When writing performance-sensitive Zig, load the DOD wiki for context:

- Primary entry point: [[Atlas/Maps/llm-wiki/data-oriented-programming/index]]
- Zig-specific patterns: [[Atlas/Maps/llm-wiki/data-oriented-programming/data-oriented-zig]] — comptime SoA generation, arena allocators, `@Vector` SIMD, packed/extern structs
- Foundations: [[Atlas/Maps/llm-wiki/data-oriented-programming/cache-locality]], [[Atlas/Maps/llm-wiki/data-oriented-programming/struct-of-arrays]], [[Atlas/Maps/llm-wiki/data-oriented-programming/existential-processing]]

Zig features that align with DOD (elaborated in the wiki):
- **No hidden allocations** — explicit `Allocator` interface
- **No vtable dispatch by default** — cache-friendly by design
- **`comptime`** — generate SoA layouts and SIMD kernels at compile time
- **`@Vector`** — first-class SIMD types for batch processing
- **Arena allocators** — bulk allocate/free for entity lifecycles

The mmap template skill below is a concrete application: flat binary formats, no pointers, dense indices — all DOD patterns.

---

## Specialized Skills

### Build System (`zig-build-system`)
**Path:** `software-development/zig-build-system/`

Zig 0.16 build system essentials: modern `build.zig` + `build.zig.zon`, the Module system, executables/libraries/tests, dependencies, and cross-compilation basics.

See `references/zig-skill-tree-design.md` for the overall philosophy and public sharing model for the Zig skill family.

Key patterns:
- `.name = .identifier` in `.zon`
- `b.addModule` / `b.createModule` + `.root_module`
- `b.addLibrary(..., .linkage = .static)`
- Proper dual test executables (`mod_tests` + `exe_tests`)

See `zig-build-system` for templates and the current recommended structure from `zig init`.

### Building from Source (`zig-build-from-source`)
**Path:** `software-development/zig-build-from-source/`

Build and install the Zig compiler from a git clone. Covers self-hosted bootstrap and CMake/LLVM fallback.

Two paths:
1. **Self-hosted** — when your installed `zig` is new enough: `zig build -Doptimize=ReleaseFast --prefix ~/.local`
2. **CMake/LLVM** — when bootstrap is too old: `cmake .. -DCMAKE_PREFIX_PATH="$(brew --prefix llvm)" && make -j`

macOS ARM64 note: `make -j$(sysctl -n hw.ncpu)` uses all performance cores. Reduce if OOM.

See `zig-build-from-source` skill for full prerequisites, install path gotchas, and PATH setup.

### Stdlib Patterns (`zig-0.16-stdlib-patterns`)
**Path:** `software-development/zig-0.16-stdlib-patterns/`

Reference for Zig 0.16 stdlib runtime APIs: HTTP client, filesystem, gzip decompression, binary parsing, SIMD.

Key patterns:
- HTTP: `client.fetch(allocator, .{ .location = .{ .url = url } })`
- Filesystem: `fs.cwd().writeFile(path, data)`, `fs.cwd().readFileAlloc(allocator, path, max)`
- Decompression: `compress.gzip.GunzipStream` (NOT `init: {}`)
- SIMD: `@Vector(8, f32)` with `@splat`, element-wise ops

See `zig-0.16-stdlib-patterns` skill for complete code patterns and common error fixes.

### Memory-Safety Review (`zig-memory-safety-review`)

Audit temporal safety, single ownership, borrow validity, pointer invalidation, cleanup, allocator domains, and concurrency protocols. The skill includes a dependency-free Python scanner that inventories review candidates without presenting heuristic matches as confirmed defects.

Use it for owner types, allocator-heavy code, C ABI boundaries, callbacks, threads, storage mutation, and PRs that change ownership or lifetimes. It extends the lightweight workflow above with ownership ledgers, call-path tracing, failure-path exercises, severity guidance, and source-grounded reporting.

See `zig-memory-safety-review` for the full workflow and scanner usage.

### mmap Template (`zig-mmap-project-template`)
**Path:** `software-development/zig-mmap-project-template/`

Create a zero-copy memory-mapped library project with flat binary formats.

Key principles:
- No pointers in structs — use byte offsets
- Separate mutable build layout from mmap snapshot layout
- Public IDs vs. dense internal indices: split into `ExternalId` (caller-facing) and `NodeIndex` (array slots)
- Compact edge storage with offset/length tables before snapshot
- `extern struct` for fixed-size headers with `comptime` size assertions

See `zig-mmap-project-template` skill for full project setup, HNSW-style graph storage patterns, and serialization.






Session-specific reference for Zig multi-agent harness architecture. Covers:
- `std.Thread.Channel` as the CSP foundation (two-thread proof-of-concept)
- Why channels beat Tokio for local multi-agent communication (no async coloring, no `!Send` foot guns, synchronous backpressure)
- What Zig stdlib provides vs. Python ergonomics for JSON and HTTP
- The selective JSON parsing opportunity (comptime field selection, incremental extraction)
- The minimal HTTP client target (bearer auth, timeout, defer-friendly cleanup)
- Proof-of-concept sequencing: validate channels first, then ergonomics layer, then orchestration



Use when building or designing a Zig-based multi-agent system.



### C API Error State and Ownership Contract


Documents `ss_last_error()` ownership semantics (caller owns returned copy, error consumed on read), the `setLastError` OOM silent failure trap and its fix, and when `page_allocator` is appropriate vs. when `DebugAllocator` produces false-positive leak reports (e.g., btree datom storage patterns).

---

## Quick Reference

| Task | Skill |
|---|---|
| New Zig project / package (build.zig + build.zig.zon) | `zig-build-system` |
| Build Zig compiler from source | `zig-build-from-source` |
| stdlib API (HTTP, fs, compress) | `zig-0.16-stdlib-patterns` |
| mmap-friendly library / data structures | `zig-mmap-project-template` |
| Memory safety, ownership, borrow, or concurrency audit | `zig-memory-safety-review` |
| General Zig 0.16 development | This skill (zig) |
| Maintaining Zig agent skills for new Zig releases | This skill (zig) + `references/updating-zig-skills-for-new-releases.md` |
