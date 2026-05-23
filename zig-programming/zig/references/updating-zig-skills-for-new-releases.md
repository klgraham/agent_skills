# Updating Zig Agent Skills for New Zig Releases

## When to Use
Run this workflow whenever the user provides a Zig skill (or its source tree) and asks to "update it for Zig X.Y.Z" or "check against the X.Y.Z language reference and std".

This captures the reproducible audit process developed while aligning the `zig-programming/` authoring tree against 0.16.0 (and cross-checked against the already-current `zig` umbrella skill).

## Standard Audit Steps
1. **Verify environment**
   - `zig version`
   - `zig env | grep std_dir` (typically `~/.local/lib/zig/std` or equivalent)
   - `zig env` for other paths if needed.

2. **Baseline with official templates**
   - `mkdir -p /tmp/zig-baseline && cd /tmp/zig-baseline && rm -rf * && zig init`
   - Inspect the freshly generated files:
     - `build.zig` (modern: `b.addModule`, `b.createModule`, `.root_module`, `addLibrary(..., .linkage=...)`, `b.addTest(.{.root_module=...})`)
     - `build.zig.zon` (`.name = .identifier`, `.minimum_zig_version`, `.paths`, fingerprint)
     - `src/main.zig` and `src/root.zig` (juicy main: `pub fn main(init: std.process.Init) !void`, use of `init.gpa`, `init.io`, `init.arena`, new `Io` writers)
   - These are the source of truth for "what a 0.16 project should look like."

3. **Inspect live stdlib for API truth**
   - Grep/read key files:
     - `std/array_list.zig` and `std.zig` → `ArrayList` now uses `.empty`, `deinit(gpa)`, `initCapacity(gpa, ...)`. Managed deprecated.
     - `std/heap.zig` and `std/heap/debug_allocator.zig` → `DebugAllocator`; `GeneralPurposeAllocator` absent.
     - `std/Build.zig` → `addLibrary`, `LibraryOptions` with `linkage`, `root_module`.
     - `std/process.zig` → `Init` struct and juicy-main contract.
     - `std/http/Client.zig`, `std/fs.zig`, etc. for fetch/cwd changes.

4. **Cross-reference official docs**
   - Language Reference: `https://ziglang.org/documentation/<ver>/`
   - Release notes: `https://ziglang.org/download/<ver>/release-notes.html` (search for "Juicy Main", I/O interface, @Type removal, build changes).
   - Use `web_search` + `web_extract` for targeted "zig <ver> <feature>".

5. **Audit the target skill**
   - Read all `SKILL.md`, `references/*.md`, `scripts/*.py` (or generators).
   - Flag every instance of:
     - `ArrayList(T).init(allocator); defer list.deinit();`
     - `GeneralPurposeAllocator`
     - `addStaticLibrary`, `root_source_file` on compile artifacts, string `.name`
     - Incomplete `main(init: std.process.Init)` that ignores the init or uses old writers
     - Missing `build.zig.zon`
     - Old `std.Io.Writer.Allocating` or pre-Io writer patterns
   - Also check for removed builtins (`@Type`), stricter lint, etc.

6. **Produce the plan**
   - Create a clear before/after table + phased task list (TDD style: update generator first, then docs, then verification).
   - Often delivered as self-contained HTML for readability (as done in the triggering session).
   - Include exact verification commands: `zig build`, `zig build test`, isolated `zig test` on snippets.

7. **Update the skill**
   - Patch `SKILL.md` (add pointer to this reference).
   - Update or add `references/`, `scripts/`, `templates/`.
   - Re-generate test projects from the updated init script and verify they build cleanly.

## Common Pitfalls (Embed in Future Runs)
- Treating the Managed container API as primary (it is deprecated and will eventually break).
- Forgetting that `zig init` now produces a multi-module layout with explicit `root_module` and a separate `root.zig`.
- Omitting `build.zig.zon` in scaffolding scripts.
- Using `page_allocator` or GPA in examples without noting the 0.16 rename.
- Assuming simple `pub fn main() !void` is the only pattern (juicy main is now the rich recommended one).
- Initial grep missing stragglers — always compile the full test suite iteratively after bulk edits.

## Related Session Knowledge (in this umbrella)
- `references/error_handling.md` — 0.16-specific errdefer and var/const strictness notes.

Use this reference when the user next asks to bring any Zig-related documentation or skill up to the current stable release. The process is deterministic and works for any future X.Y.Z bump.