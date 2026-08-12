# Zig Programming Skills

A collection of specialized, high-signal agent skills for writing, debugging, reviewing, and building production Zig code on Zig 0.16+.

These skills follow a **narrow, focused** design instead of one large monolithic skill. Each skill owns a specific domain so the agent (and humans) can load only what they need.

## Skills in This Collection

| Skill | Purpose | When to Load |
|-------|---------|--------------|
| **zig** | Lightweight hub + 0.16 gotchas, memory safety workflow, cross-links | General Zig 0.16 development, migration help, "what changed" |
| **zig-build-system** | Modern `build.zig` + `build.zig.zon`, Module system, executables/libraries/tests, dependencies | Setting up or modernizing projects, cross-compilation, package manifests |
| **zig-0-16-stdlib-patterns** | Current stdlib runtime APIs (HTTP, fs, compress, etc.) and 0.15→0.16 differences | Working with `std.http`, `std.fs`, `std.compress`, allocators, writers |
| **zig-build-from-source** | Building the Zig compiler itself (self-hosted vs CMake path) | When you need a newer Zig or want to contribute to the compiler |
| **zig-data-oriented-programming** | SoA, `@Vector` SIMD, arena patterns, cache-friendly design | Performance-sensitive code, hot loops, bulk data processing |
| **zig-mmap-project-template** | Zero-copy memory-mapped data structures, flat binary formats | Building high-performance libraries with mmap-backed storage |
| **zig-memory-safety-review** | Ownership, borrow lifetime, invalidation, cleanup, and concurrency audit workflow with a bundled heuristic scanner | Reviewing allocators, owner types, C ABI code, callbacks, threads, or memory-safety-sensitive PRs |
| **write-legible-zig** | Machine-legible Zig structure, naming, error handling, ownership boundaries, and verification checklist | Creating, editing, reviewing, or presenting Zig code that should be easy for agents and humans to change |

## Recommended Usage

1. Copy the skill directories you want into your agent's skills folder. For Hermes Agent, for example:
   ```bash
   cp -r zig-build-system ~/.hermes/skills/software-development/
   ```

2. The `zig` skill acts as the entry point and router — start there for most tasks.

3. Load `write-legible-zig` for every Zig code change, then add the narrow skill for the task's domain.
4. For the latest patterns, always prefer the narrow skills over older generalist documentation.

## Philosophy

- **Specialized > Monolithic**: Each skill stays small, up-to-date, and easy to maintain.
- **Practical first**: Heavy emphasis on copy-pasteable code + "what changed in 0.16" notes.
- **Tested on real work**: Born from migrating, reviewing, and building systems-level Zig projects.

## Contributing / Updating

These skills are maintained against the current stable Zig release. When a new Zig version ships:

1. Run the audit workflow documented in `zig/references/updating-zig-skills-for-new-releases.md`
2. Update the affected narrow skills and their trigger metadata
3. Validate the skills and test code examples with real projects

## License

MIT (same as the individual skills)

---

Maintained by klogram. Feedback and PRs welcome.
