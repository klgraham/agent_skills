# Zig programming

A single router skill containing principles, focused playbooks, references, scripts, and runnable examples for **Zig 0.16.0**.

Start with [SKILL.md](SKILL.md). It selects only the resources needed for the task instead of installing eight independent skills.

## Layout

```text
SKILL.md        Router and version contract
playbooks/      Intent-specific procedures
principles/     Allocator, error, C ABI, and comptime guidance
references/     Conditional deep dives and the legibility standard
examples/       Runnable Zig contracts
scripts/        Example verifier and memory-safety scanner
```

## Validate

From this directory, with Zig 0.16.0 and Python 3:

```bash
python3 scripts/verify_examples.py
python3 scripts/verify_examples.py --io-only
python3 scripts/test_zig_memory_safety_scan.py
```

Use `--zig /absolute/path/to/zig` for another installation of 0.16.0. The example verifier uses a temporary workspace and cache. It runs ownership, allocation-failure, binary-boundary, SIMD, comptime, streams, and concurrency tests; checks an intentional compile failure; exercises runtime file and gzip behavior; builds a C-linked generated-file project; and performs a cross-target compilation. HTTP is compiled but not requested. Evented I/O backends are documented but not exercised.

## Sources and maintenance

The collection is reviewed against the [0.16.0 language reference](https://ziglang.org/documentation/0.16.0/), [build guide](https://ziglang.org/learn/build-system/), release notes, and the installed 0.16.0 SDK. The build guide can change independently of the pinned release.

Follow [the release-update playbook](playbooks/update-zig-release.md) for future versions. Run the Claude plugin validator, check relative links, and compile the examples before publishing changes. MIT license applies to this collection.
