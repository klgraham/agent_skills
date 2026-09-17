# Update this collection for a Zig release

1. Record the requested version and inspect the project pin, `zig version`,
   and `zig env`. Treat development snapshots as distinct toolchains.
2. Read the versioned language reference, release notes, and official build
   guide. The build guide is not versioned. Resolve contradictions with the
   pinned compiler and its source rather than copying either page blindly.
3. Run `zig init` in a newly created temporary directory. Inspect the generated
   manifest, modules, runtime entry point, and test steps.
4. Review every playbook, principle, and linked reference. Search for affected APIs,
   including runtime I/O, containers, type constructors, build options, and
   platform mapping calls. Preserve useful principles; replace unsupported recipes.
5. Update runnable examples and their verifier alongside the guidance. Keep
   intentional compile-failure cases separate from valid examples.
6. Validate the root `SKILL.md` frontmatter. Check relative links and the
   provider-package symlink. Copy the provider package with symlinks
   dereferenced and validate its contents too.
7. Run `python3 scripts/verify_examples.py` from the collection directory.
   Update its exact-version gate only when changing the collection's target.
8. Run the existing memory-safety scanner tests if its packaging or behavior
   changed. Inspect the final diff and report checks that were not performed.

Do not change unsupported historical claims into new version claims by search
and replace. `zig ast-check` checks syntax and some early constraints; it is
not a replacement for semantic compilation and execution. A cross-compiled
artifact is not a tested target runtime.

Primary sources for the current baseline:
- [Language reference](https://ziglang.org/documentation/0.16.0/)
- [Build guide](https://ziglang.org/learn/build-system/)
- [Release notes](https://ziglang.org/download/0.16.0/release-notes.html)
- Installed SDK source located using `zig env`
