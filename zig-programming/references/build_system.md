# Zig Build System Reference

## Basic build.zig Structure

```zig
const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    
    const exe = b.addExecutable(.{
        .name = "myapp",
        .root_source_file = b.path("src/main.zig"),
        .target = target,
        .optimize = optimize,
    });
    
    b.installArtifact(exe);
    
    const run_cmd = b.addRunArtifact(exe);
    run_cmd.step.dependOn(b.getInstallStep());
    
    const run_step = b.step("run", "Run the app");
    run_step.dependOn(&run_cmd.step);
}
```

## Common Build Patterns

### Adding a Static Library
```zig
const lib = b.addStaticLibrary(.{
    .name = "mylib",
    .root_source_file = b.path("src/lib.zig"),
    .target = target,
    .optimize = optimize,
});
b.installArtifact(lib);
```

### Adding Tests
```zig
const unit_tests = b.addTest(.{
    .root_source_file = b.path("src/main.zig"),
    .target = target,
    .optimize = optimize,
});

const run_unit_tests = b.addRunArtifact(unit_tests);

const test_step = b.step("test", "Run unit tests");
test_step.dependOn(&run_unit_tests.step);
```

### Linking C Libraries
```zig
exe.linkSystemLibrary("c");
exe.linkSystemLibrary("sqlite3");
```

### Adding Dependencies
```zig
const dep = b.dependency("mydep", .{
    .target = target,
    .optimize = optimize,
});

exe.root_module.addImport("mydep", dep.module("mydep"));
```

### Adding Include Paths
```zig
exe.addIncludePath(b.path("include"));
exe.addCSourceFile(.{
    .file = b.path("src/bindings.c"),
    .flags = &[_][]const u8{"-std=c99"},
});
```

### Cross-Compilation
```zig
const target = b.resolveTargetQuery(.{
    .cpu_arch = .aarch64,
    .os_tag = .linux,
});
```

## Build Options

### Creating Build Options
```zig
const config = b.addOptions();
config.addOption(bool, "enable_logging", true);
config.addOption([]const u8, "version", "1.0.0");

exe.root_module.addOptions("config", config);
```

### Using Build Options in Code
```zig
const config = @import("config");

if (config.enable_logging) {
    std.log.info("Version: {s}", .{config.version});
}
```

## Build Modes

- **Debug** (`-Ddebug`): No optimizations, safety checks enabled
- **ReleaseSafe** (`-Doptimize=ReleaseSafe`): Optimized with safety checks
- **ReleaseFast** (`-Doptimize=ReleaseFast`): Maximum performance, no safety
- **ReleaseSmall** (`-Doptimize=ReleaseSmall`): Optimized for size

## Common Build Commands

```bash
# Build the project
zig build

# Run the executable
zig build run

# Run tests
zig build test

# Clean build artifacts
rm -rf zig-cache zig-out

# Build for specific target
zig build -Dtarget=x86_64-windows

# Build with specific optimization
zig build -Doptimize=ReleaseFast
```

## Module System

### Creating a Module
```zig
const mymodule = b.addModule("mymodule", .{
    .root_source_file = b.path("src/mymodule.zig"),
});

exe.root_module.addImport("mymodule", mymodule);
```

### Using in Code
```zig
const mymodule = @import("mymodule");
```
