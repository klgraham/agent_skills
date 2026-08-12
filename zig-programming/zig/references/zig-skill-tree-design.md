# Zig Skill Family Design (2026)

## Core Principle

For a complex, fast-evolving domain like Zig (especially around 0.16+ releases), maintain **narrow, class-level specialized skills** rather than large monolithic or generalist skills.

## Recommended Structure

- **zig** (hub)
  - Lightweight
  - Owns: high-signal gotchas, memory safety workflow, design philosophy, quick-reference table, cross-links
  - Rich `references/` for durable process knowledge (e.g. release update audit, error handling patterns)

- Narrow specialized siblings (each with its own rich SKILL.md + `references/`):
  - `write-legible-zig`
  - `zig-build-system`
  - `zig-0-16-stdlib-patterns`
  - `zig-build-from-source`
  - `zig-data-oriented-programming`
  - `zig-mmap-project-template`
  - `zig-memory-safety-review`
  - Future narrow skills as gaps appear

## Public Sharing Model

The working copies live in `~/.hermes/skills/software-development/zig*`.

For GitHub sharing with other developers:
- Use `~/dev/klogram_labs/agent_skills/zig-programming/` as the clean public mirror.
- Populate it with the same narrow skill directories (no monolithic `zig-programming` skill).
- Add a root `README.md` explaining the collection and copy instructions.
- Old monolithic attempts (the original `zig-programming/` content) are archived.

This keeps private working state (project-specific notes, long references) out of the public tree while still allowing high-quality, reusable skills to be shared.

## Why This Shape

- Narrow skills stay accurate and are easy to keep current when Zig releases change.
- The hub stays small and high-signal.
- Agents load only what they need.
- Public sharing becomes trivial and maintainable.

## When Evolving the Tree

- New capability → new narrow skill (never enlarge the hub or create another generalist).
- Major release → run the audit process in `references/updating-zig-skills-for-new-releases.md`.
- Public mirror drifts → re-mirror from the authoritative `~/.hermes` copies.

This decision was made during the 0.16.0 `zig-programming/` audit and `zig-build-system` creation session.
