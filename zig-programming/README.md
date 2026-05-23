# Zig Skills for Hermes Agent

A collection of specialized, high-signal skills for writing, debugging, and building production Zig code on Zig 0.16+.

These skills follow a **narrow, focused** design instead of one large monolithic skill. Each skill owns a specific domain so the agent (and humans) can load only what they need.

## Skills in This Collection

| Skill | Purpose | When to Load |
|-------|---------|--------------|
| **zig** | Lightweight hub + 0.16 gotchas, memory safety workflow, cross-links | General Zig 0.16 development, migration help, "what changed" |
| **zig-build-system** | Modern `build.zig` + `build.zig.zon`, Module system, executables/libraries/tests, dependencies | Setting up or modernizing projects, cross-compilation, package manifests |
| **zig-0.16-stdlib-patterns** | Current stdlib runtime APIs (HTTP, fs, compress, etc.) and 0.15→0.16 differences | Working with `std.http`, `std.fs`, `std.compress`, allocators, writers |
| **zig-build-from-source** | Building the Zig compiler itself (self-hosted vs CMake path) | When you need a newer Zig or want to contribute to the compiler |
| **zig-data-oriented-programming** | SoA, `@Vector` SIMD, arena patterns, cache-friendly design | Performance-sensitive code, hot loops, bulk data processing |
| **zig-mmap-project-template** | Zero-copy memory-mapped data structures, flat binary formats | Building high-performance libraries with mmap-backed storage |

## Recommended Usage

1. Copy the skill directories you want into your Hermes skills folder:
   ```bash
   cp -r zig-build-system ~/.hermes/skills/software-development/
   ```

2. The `zig` skill acts as the entry point and router — start there for most tasks.

3. For the latest patterns, always prefer the narrow skills over older generalist documentation.

## Philosophy

- **Specialized > Monolithic**: Each skill stays small, up-to-date, and easy to maintain.
- **Practical first**: Heavy emphasis on copy-pasteable code + "what changed in 0.16" notes.
- **Tested on real work**: Born from migrating and building systems-level Zig projects (including Ken's personal projects).

## Contributing / Updating

These skills are maintained against the current stable Zig release. When a new Zig version ships:

1. Run the audit workflow documented in `zig/references/updating-zig-skills-for-new-releases.md`
2. Update the affected narrow skills
3. Bump versions and test with real projects

## License

MIT (same as the individual skills)

---

Maintained by klogram. Feedback and PRs welcome.