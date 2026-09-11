---
name: zig-build-system
description: "Zig 0.16.0 build and release playbooks. Use for build.zig, package manifests, modules, C sources, generated files, dependencies, test graphs, cross-compilation, and release artifacts."
license: MIT
metadata:
  hermes:
    tags: [zig, build-system, build.zig, zig-0.16]
    category: software-development
    skill_type: reference
---

# Builds and releases with Zig 0.16.0

Use for application and library builds. For the compiler itself, use
[build from source](../zig-build-from-source/SKILL.md).

## Principles

Model generated inputs and outputs as dependencies. Use `LazyPath` values
instead of guessing paths under `.zig-cache`. Respect the caller's install
prefix. Separate host tools from target artifacts and compilation from execution.

Keep graph configuration free of incidental writes, downloads, and tool runs.
Declare those operations as steps so caching and scheduling can account for them.
Make changes to tracked generated source an explicit update step.

## Playbook: create or modernize a project

1. Run the pinned `zig init` in a new scratch directory. Compare its manifest
   and module structure with the project; do not overwrite existing files.
2. Use `b.standardTargetOptions(.{})` and `b.standardOptimizeOption(.{})`.
   Carry the selected settings into the modules that compile the code.
3. Use `b.addModule` to expose a module to package consumers and
   `b.createModule` for an internal module. Give artifacts `.root_module`.
4. Install executables or libraries explicitly. For static libraries use
   `b.addLibrary` with `.linkage = .static`.
5. Pair `b.addTest` with `b.addRunArtifact` for runnable native tests. Wire
   integration roots explicitly. A named test step with no reachable tests
   can succeed without testing the feature.
6. Forward `b.args` to a run step when the program accepts arguments.

The [example build](../zig/examples/project/build.zig) includes a public module,
C helper, host generator, run step, native tests, and a compile-only check step.
Copy its directory to a scratch location and run:

```bash
zig build
zig build test --summary all
zig build run
zig build check -Dtarget=x86_64-linux-musl
zig build --help
```

The cross-target `check` compiles tests without executing foreign binaries.
Old `addStaticLibrary` and artifact-level `.root_source_file` recipes are not
valid replacements for the 0.16.0 Module API.

## Playbook: package dependencies

Start `build.zig.zon` from `zig init`. Keep its stable fingerprint, package name,
version, minimum compiler version, dependencies, and source paths coherent.
The minimum version is not an exact toolchain pin; pin the compiler separately
in project tooling and CI. Include every build input in `.paths`, including
headers and generator sources. Test the packaged tree without undeclared files.

Resolve dependencies with `b.dependency`, passing the relevant target and
optimization options. Import their published modules or link their artifacts.
For URL dependencies, retain the package hash produced by Zig tooling.
A hash identifies content; it does not establish that a dependency is trustworthy.
Do not invent hashes or package fingerprints for copyable templates.

## Playbook: generate an input

Compile a generator for `b.graph.host`, even during cross-compilation. Supply
source inputs with `addFileArg` and outputs with `addOutputFileArg` or
`addOutputDirectoryArg`. Feed the resulting `LazyPath` into the consuming
module, file copy, or install step. `addWriteFiles` fits small generated files
that do not require a tool. Add options through `b.addOptions` for typed build
configuration. Prefer explicit input dependencies to unconditional execution.

The example's generator produces an anonymous import consumed by `@embedFile`.
Test a changed input as well as a repeated unchanged build. Check generated
files under a different install prefix to catch hardcoded paths.

## Playbook: prepare a release

1. Define supported target triples, minimum OS or libc versions, CPU baseline,
   and runtime dependencies. Cross-compilation does not bundle every SDK or
   system library, and it does not prove the artifact runs on that target.
2. Choose an optimization mode for the product's contract. Debug and ReleaseSafe
   retain runtime safety checks by default. ReleaseFast and ReleaseSmall disable
   them by default; explicit input validation remains necessary in every mode.
3. Run native tests with safety checks and the intended shipping mode. Build
   each target separately and execute smoke tests on available target systems.
4. Install under distinct prefixes, or use `addInstallArtifact` with a
   target-specific destination. Never let same-named artifacts overwrite one another.
5. Package the installed files with licenses and required runtime files.
   Record compiler version, source revision, target, CPU, mode, and checksums.
6. Inspect and smoke-test the extracted archive. Publish only within the user's
   requested release scope; building a release does not itself request a tag or upload.

For the bundled example, a compile-only Linux release check is:

```bash
zig build -Dtarget=x86_64-linux-musl -Doptimize=ReleaseSafe --prefix out/linux
```

## Sources and validation

The [official build guide](https://ziglang.org/learn/build-system/) explains
step dependencies, generated files, and target-specific installation. It is a
living page; recheck examples against 0.16.0. Inspect `std/Build.zig`,
`std/Build/Module.zig`, and `std/Build/Step/Run.zig` for exact contracts.
The collection's [verifier](../zig/scripts/verify_examples.py) runs the bundled
project, checks a changed generator input, and cross-compiles its check step.
