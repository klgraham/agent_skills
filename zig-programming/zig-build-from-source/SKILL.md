---
name: zig-build-from-source
description: "Build and install the Zig compiler from a git clone. Covers the self-hosted `zig build` path and the CMake/LLVM fallback when the bootstrap compiler is too old. Targets macOS (Apple Silicon) with Homebrew LLVM, but patterns generalize."
license: MIT
metadata:
  hermes:
    tags: [zig, build-from-source, compiler, toolchain, bootstrap, macos, llvm, cmake]
    category: software-development
    skill_type: workflow
---

# Build and Install Zig from Source

Use when you need to build the Zig compiler itself from a git clone, or when an existing dev build is too old to bootstrap the release you want.

## Quick Reference

| Path | Command | When to use |
|---|---|---|
| Self-hosted bootstrap | `zig build -Doptimize=ReleaseFast --prefix ~/.local` | Your installed `zig` is new enough to build the target tag |
| CMake/LLVM fallback | `cmake .. -DCMAKE_PREFIX_PATH="$(brew --prefix llvm)" && make -j$(sysctl -n hw.ncpu)` | Self-hosted bootstrap fails due to missing new OS targets |

## 1. Self-Hosted Bootstrap (Preferred)

If your installed `zig` is a recent dev build of the same minor version:

```bash
cd ~/zig   # or ~/dev/zig
git fetch origin
git checkout 0.16.0   # or any tag/branch
zig build -Doptimize=ReleaseFast --prefix ~/.local
~/.local/bin/zig version
```

This is the fastest path. The build system compiles stage3 and installs it.

## 2. CMake/LLVM Fallback (macOS Apple Silicon)

Use this when `zig build` fails with errors like:

```
error: enum 'Target.Os.Tag' has no member named 'psp'
```

This means your bootstrap compiler predates the target additions in the release. You need a C++ bootstrap via CMake and LLVM.

### Prerequisites

- CMake (`brew install cmake`)
- Homebrew LLVM (`brew install llvm`)
- Xcode Command Line Tools (Apple Clang)

### Build Commands

```bash
cd ~/zig   # your git clone
git checkout 0.16.0

mkdir -p build-release && cd build-release

cmake .. \
  -DCMAKE_PREFIX_PATH="$(brew --prefix llvm)" \
  -DCMAKE_BUILD_TYPE=Release \
  -DZIG_STATIC_LLVM=OFF

make -j$(sysctl -n hw.ncpu)
```

The build produces:
- `zig1` — C transpiled bootstrap (from `stage1/zig1.wasm`)
- `zig2` — C++ host compiler built by `zig1`
- `stage3/bin/zig` — final self-hosted compiler built by `zig2`

### Install

**Do NOT use `make install DESTDIR`** — it creates a nested path under `$HOME/.local/Users/...`.

Instead, copy directly:

```bash
mkdir -p ~/.local/bin ~/.local/lib/zig
cp stage3/bin/zig ~/.local/bin/zig
cp -r stage3/lib/zig/* ~/.local/lib/zig/ 2>/dev/null || cp -r ../lib/std ~/.local/lib/zig/
chmod +x ~/.local/bin/zig
~/.local/bin/zig version   # → 0.16.0
```

## 3. PATH Setup

If `~/.local/bin` is not in your PATH:

```bash
# Add to ~/.zshrc (or ~/.bash_profile)
export PATH="$HOME/.local/bin:$PATH"
```

## Common Failures

### "enum has no member named 'psp'" (or other missing OS target)

Your bootstrap `zig` is too old. Switch to the CMake/LLVM path (Section 2).

### CMake can't find LLVM/Clang/LLD

Ensure Homebrew LLVM is linked in the prefix path:

```bash
cmake .. -DCMAKE_PREFIX_PATH="$(brew --prefix llvm)"
```

### "zig: command not found" after install

```bash
which zig          # may show the old path
hash -r            # clear shell command cache
~/.local/bin/zig version
```

## Verification

```bash
zig version        # should match the tag exactly, e.g. 0.16.0
zig targets        # should list the new targets (e.g. psp)
zig build --help   # confirms the toolchain is functional
```

## Notes

- On macOS ARM64, `make -j$(sysctl -n hw.ncpu)` uses all performance cores. The build is memory-heavy; if OOM occurs, reduce parallelism: `make -j4`.
- The `stage3` binary is the one you want. `zig1` and `zig2` are intermediate bootstraps.
- `ReleaseFast` produces the fastest compiler. `ReleaseSafe` leaves safety checks in but is slower.
- The `lib/` directory contains the Zig standard library and compiler runtime. It must remain accessible to the binary.
