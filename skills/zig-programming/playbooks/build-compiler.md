# Build the Zig compiler from source

Use for compiler development or a toolchain that must be built locally. For
normal project builds, use [the project build playbook](build-project.md).

## Principles

Pin the source revision and bootstrap dependencies together. A nearby version
number does not prove a compiler can bootstrap a checkout. Follow that revision's
README, CMake configuration, and CI rather than assuming the system LLVM matches.
Install into a separate prefix before changing the user's active toolchain.

## Playbook

1. Inspect the source checkout's status and revision. Use a separate checkout
   for another tag when local work exists. Do not reset or overwrite it.
2. Read its documented build prerequisites and available build options. If an
   existing Zig can build that revision, use the documented self-hosted route.
3. Otherwise follow the revision's CMake or bootstrap route. Pin LLVM, Clang,
   and LLD to compatible versions, with matching development libraries.
4. Configure a fresh build directory and a dedicated install prefix. Use
   `cmake --build` and `cmake --install` for a CMake build. `DESTDIR` stages an
   existing install prefix; it does not replace `CMAKE_INSTALL_PREFIX`.
5. Keep the compiler binary with its complete installed `lib` tree. Do not
   recover a failed install by copying only `lib/std` and ignoring errors.
6. Run the new binary by absolute path. Check `version` and `env`, initialize a
   scratch project, build it, and run its tests. Record the source revision and
   bootstrap toolchain. Change PATH only if requested.

If a bootstrap reports an unknown target or missing API, check version
compatibility first. If CMake cannot find libraries, check dependency versions
and prefixes before changing compiler sources. Reduce parallelism when memory
pressure, rather than a compiler diagnostic, terminates the build.

The [0.16.0 release notes](https://ziglang.org/download/0.16.0/release-notes.html)
identify LLVM 21.1.0 for that release. A newer source checkout can require a
different version. The [Zig source](https://codeberg.org/ziglang/zig) README and
build configuration at the selected revision are the build authority.

This playbook does not claim that a full compiler bootstrap was executed by the
skill example verifier; that verifier tests use of the installed compiler.
