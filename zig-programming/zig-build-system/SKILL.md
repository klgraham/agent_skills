---
name: zig-build-system
description: "Zig 0.16 build system essentials: modern build.zig + build.zig.zon patterns, the Module system, executables/libraries/tests, dependencies, and cross-compilation. Use when setting up new Zig projects or modernizing build files."
license: MIT
metadata:
  hermes:
    tags: [zig, build-system, build.zig, zig-0.16]
    category: software-development
    skill_type: reference
---

# Zig Build System (0.16 Essentials)

Focused reference for writing and maintaining `build.zig` / `build.zig.zon` in Zig 0.16.

## When to Use

- Creating a new Zig executable, library, or package
- Updating old `build.zig` files to current patterns
- Adding dependencies or exposing modules
- Cross-compiling or configuring optimization / targets
- Understanding why `zig init` produces the structure it does

Do **not** use for:
- Building the Zig compiler itself (see `zig-build-from-source`)
- Deep stdlib runtime patterns (see `zig-0-16-stdlib-patterns`)

## Canonical Project Layout (from `zig init`)

Run `zig init` in an empty directory to get the current recommended structure:

```
myproject/
├── build.zig
├── build.zig.zon
├── src/
│   ├── main.zig
│   └── root.zig
└── .gitignore
```

This layout uses the modern **Module** system instead of the older `root_source_file` + per-artifact target/optimize approach.

## build.zig.zon (Package Manifest)

```zig
.{
    .name = .myproject,                    // identifier, not string
    .version = "0.1.0",
    .fingerprint = 0x...,                  // stable identity
    .minimum_zig_version = "0.16.0",
    .dependencies = .{
        // .example = .{ .url = "...", .hash = "..." },
    },
    .paths = .{
        "build.zig",
        "build.zig.zon",
        "src",
        // "LICENSE",
    },
}
```

**Important**:
- `.name` uses the dot-identifier form (`.myproject`)
- `.fingerprint` is generated once and should rarely change
- Always include `build.zig.zon` in `.paths`

## build.zig — Modern Structure

```zig
const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    // 1. Define a module you want to expose to consumers
    const mod = b.addModule("myproject", .{
        .root_source_file = b.path("src/root.zig"),
        .target = target,
    });

    // 2. Executable that uses the module
    const exe = b.addExecutable(.{
        .name = "myproject",
        .root_module = b.createModule(.{
            .root_source_file = b.path("src/main.zig"),
            .target = target,
            .optimize = optimize,
            .imports = &.{
                .{ .name = "myproject", .module = mod },
            },
        }),
    });

    b.installArtifact(exe);

    // Run step
    const run_cmd = b.addRunArtifact(exe);
    const run_step = b.step("run", "Run the app");
    run_step.dependOn(&run_cmd.step);

    // Tests (two executables recommended)
    const mod_tests = b.addTest(.{ .root_module = mod });
    const exe_tests = b.addTest(.{ .root_module = exe.root_module });

    const test_step = b.step("test", "Run tests");
    test_step.dependOn(&b.addRunArtifact(mod_tests).step);
    test_step.dependOn(&b.addRunArtifact(exe_tests).step);
}
```

### Key 0.16 Patterns

- Use `b.addModule()` for modules you want to expose.
- Use `b.createModule()` for internal-only modules (executables, tests).
- Prefer `.root_module` over the old `root_source_file` + `target`/`optimize` fields on `addExecutable`/`addTest`.
- Libraries: `b.addLibrary(.{ .name = "...", .root_module = ..., .linkage = .static })`

### Adding a Static Library

```zig
const lib = b.addLibrary(.{
    .name = "mylib",
    .root_module = b.createModule(.{
        .root_source_file = b.path("src/lib.zig"),
        .target = target,
        .optimize = optimize,
    }),
    .linkage = .static,
});

b.installArtifact(lib);
```

## Dependencies

```zig
const dep = b.dependency("some_dep", .{
    .target = target,
    .optimize = optimize,
});

exe.root_module.addImport("some_dep", dep.module("some_dep"));
```

In `build.zig.zon`:
```zig
.dependencies = .{
    .some_dep = .{
        .url = "https://.../archive/...tar.gz",
        .hash = "...",
    },
},
```

## Common Steps & Commands

```bash
zig build                 # default (install)
zig build run
zig build test
zig build -Doptimize=ReleaseFast
zig build --help          # shows all steps and options
```

## Cross Compilation

```zig
const target = b.resolveTargetQuery(.{
    .cpu_arch = .aarch64,
    .os_tag = .linux,
});

const exe = b.addExecutable(.{
    .name = "myapp",
    .root_module = b.createModule(.{
        .root_source_file = b.path("src/main.zig"),
        .target = target,
        .optimize = optimize,
    }),
});
```

## Common Pitfalls (0.16)

- Using old `addStaticLibrary(...)` or `root_source_file` on compile artifacts — these still work in some cases but are no longer the recommended style.
- Forgetting `build.zig.zon` when publishing a package.
- Mixing `b.addModule` (public) and `b.createModule` (private) incorrectly.
- Putting `.name = "foo"` (string) instead of `.name = .foo` (identifier) in `.zon`.
- Forgetting to wire both `mod_tests` and `exe_tests` when you have a separate root module.

## Verification

After changing a `build.zig`:

```bash
zig build
zig build test
zig build --help
```

For a new project:

```bash
mkdir testproj && cd testproj
zig init
zig build
zig build test
```

## Related Skills

- `zig` (hub) — overall 0.16 gotchas and memory safety
- `zig-0-16-stdlib-patterns`
- `zig-build-from-source`
- `zig-mmap-project-template`

Use this skill when the pain is in the build graph rather than the language or stdlib itself.
