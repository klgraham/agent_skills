# Zig programming skills

Principles and practical playbooks for **Zig 0.16.0**. Start with
[zig](zig/SKILL.md) and load only the topics needed for the task.

| Skill | Focus |
|---|---|
| [zig](zig/SKILL.md) | Entry point; allocator choice, errors, C interop, and comptime references |
| [zig-build-system](zig-build-system/SKILL.md) | Modules, dependencies, generated files, tests, cross-compilation, releases |
| [zig-0-16-stdlib-patterns](zig-0-16-stdlib-patterns/SKILL.md) | `std.Io` streams/formatting, futures/groups, cancellation, queues, locks, parallel work, HTTP, ArrayList |
| [zig-build-from-source](zig-build-from-source/SKILL.md) | Pinned compiler bootstrap and installation |
| [zig-data-oriented-programming](zig-data-oriented-programming/SKILL.md) | Layout decisions, SIMD, scalar baselines, and measurement |
| [zig-mmap-project-template](zig-mmap-project-template/SKILL.md) | Validated binary formats, mapping lifetimes, graph snapshots |
| [zig-memory-safety-review](zig-memory-safety-review/SKILL.md) | Ownership, invalidation, rollback, callbacks, concurrency, heuristic scanner |
| [write-legible-zig](write-legible-zig/SKILL.md) | Naming, state, error paths, ownership, and review standard |

Install the collection's sibling directories together to preserve relative
links. The Claude plugin uses symlinks to these canonical directories. Skill
entrypoints contain routing and core decisions; references contain conditional
playbooks, and runnable examples live in `zig/examples/`.

## Validate the examples

From this directory, with Zig 0.16.0 and Python 3:

```bash
python3 zig/scripts/verify_examples.py
python3 zig/scripts/verify_examples.py --io-only
```

Use `--zig /absolute/path/to/zig` for another installation of 0.16.0. The verifier
uses a temporary workspace and cache. It runs ownership, allocation-failure,
binary-boundary, SIMD, comptime, streams, and concurrency tests; checks an intentional compile failure;
runs runtime file and gzip checks; exercises a C-linked generated-file build;
and performs a cross-target compilation. HTTP is compiled but not requested.
Concurrency tests include inline execution, launch refusal, cancellation,
Select, queues, locks, and bounded workers, with a timeout to catch deadlocks.
Evented backends are documented but not exercised. The verifier does not
benchmark performance, bootstrap a compiler, or prove mmap safety.

## Sources and maintenance

Reviewed against the [0.16.0 language reference](https://ziglang.org/documentation/0.16.0/),
[build guide](https://ziglang.org/learn/build-system/), release notes, and the
installed 0.16.0 SDK. References name the relevant library source files.
The build guide can change independently of the pinned release.

Follow the [release-update playbook](zig/references/updating-zig-skills-for-new-releases.md)
for future versions. Run the skill-creator validator and check packaged links
as well as compiling examples. MIT license applies to this collection.
