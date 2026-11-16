# Zig programming

A single router skill containing principles, focused playbooks, references, scripts, and runnable examples for **Zig 0.17.1**.

Start with [SKILL.md](SKILL.md) and follow the route for your task. For I/O and
concurrency design, [Use std.Io](playbooks/use-io.md) maps common needs to procedures.

## Layout

```text
SKILL.md        Router and version contract
playbooks/      Procedures for specific tasks
principles/     Design rules for allocation, errors, C ABI, comptime, and I/O
references/     API contracts and the legibility standard
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

Use `--zig /absolute/path/to/zig` to select a 0.17.1 installation. The verifier
uses a temporary workspace and cache. It exercises ownership, allocation failure,
binary parsing, SIMD, comptime, files, gzip, and streams. Its concurrency tests
cover tasks, worker pools, chunked reduction, channel pipelines, and an actor
on threaded and inline configurations. It also checks an intentional compile
failure, C linkage, generated inputs, and argument forwarding. Linux and HTTP
are compile checks. Concurrency runtime coverage is for `Io.Threaded`.

## Sources and maintenance

The [release-update playbook](playbooks/update-zig-release.md) lists the sources for the current baseline. Check language rules against the versioned reference and library signatures against the installed SDK. The build guide can change independently of the pinned release.

Run the Claude plugin validator, check relative links, and compile the examples before publishing changes. MIT license applies to this collection.
