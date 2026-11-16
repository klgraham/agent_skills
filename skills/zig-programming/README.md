# Zig programming

A single router skill containing principles, focused playbooks, references, scripts, and runnable examples for **Zig 0.17.1**.

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

From this directory, with Zig 0.17.1 and Python 3:

```bash
python3 scripts/verify_examples.py
python3 scripts/verify_examples.py --io-only
python3 scripts/test_zig_memory_safety_scan.py
```

Use `--zig /absolute/path/to/zig` to select a 0.17.1 installation. The verifier uses a temporary workspace and cache. It runs ownership, allocation failure, binary parsing, SIMD, comptime, streams, and concurrency tests; checks an intentional compile failure; exercises file and gzip behavior; and checks C linkage, generated inputs, and argument forwarding in the sample project. It compiles for Linux without running the Linux artifact. It compiles HTTP code without sending requests and does not exercise evented I/O backends.

## Sources and maintenance

The [release-update playbook](playbooks/update-zig-release.md) lists the sources for the current baseline. Check language rules against the versioned reference and library signatures against the installed SDK. The build guide can change independently of the pinned release.

Run the Claude plugin validator, check relative links, and compile the examples before publishing changes. MIT license applies to this collection.
