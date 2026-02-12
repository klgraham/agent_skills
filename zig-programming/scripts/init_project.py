#!/usr/bin/env python3
"""
Script to initialize a new Zig project with standard structure.
"""
import os
import sys
from pathlib import Path


def create_main_zig() -> str:
    """Generate main.zig content."""
    return '''const std = @import("std");

pub fn main(init: std.process.Init) !void {
    std.debug.print("Hello, World!\\n", .{});
}

test "basic test" {
    try std.testing.expect(2 + 2 == 4);
}
'''


def create_build_zig() -> str:
    """Generate build.zig content."""
    return '''const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const exe = b.addExecutable(.{
        .name = "app",
        .root_source_file = b.path("src/main.zig"),
        .target = target,
        .optimize = optimize,
    });

    b.installArtifact(exe);

    const run_cmd = b.addRunArtifact(exe);
    run_cmd.step.dependOn(b.getInstallStep());

    if (b.args) |args| {
        run_cmd.addArgs(args);
    }

    const run_step = b.step("run", "Run the app");
    run_step.dependOn(&run_cmd.step);

    const unit_tests = b.addTest(.{
        .root_source_file = b.path("src/main.zig"),
        .target = target,
        .optimize = optimize,
    });

    const run_unit_tests = b.addRunArtifact(unit_tests);

    const test_step = b.step("test", "Run unit tests");
    test_step.dependOn(&run_unit_tests.step);
}
'''


def create_gitignore() -> str:
    """Generate .gitignore content."""
    return '''zig-cache/
zig-out/
.zig-cache/
*.o
*.a
*.so
*.dylib
*.exe
'''


def create_readme(project_name: str) -> str:
    """Generate README.md content."""
    return f'''# {project_name}

A Zig project.

## Building

```bash
zig build
```

## Running

```bash
zig build run
```

## Testing

```bash
zig build test
```

## Project Structure

- `src/` - Source files
- `build.zig` - Build configuration
'''


def init_project(project_name: str, path: str = ".") -> None:
    """Initialize a new Zig project."""
    project_path = Path(path) / project_name
    src_path = project_path / "src"
    
    # Create directories
    src_path.mkdir(parents=True, exist_ok=True)
    
    # Create files
    files = {
        "build.zig": create_build_zig(),
        "src/main.zig": create_main_zig(),
        ".gitignore": create_gitignore(),
        "README.md": create_readme(project_name),
    }
    
    for file_path, content in files.items():
        full_path = project_path / file_path
        full_path.write_text(content)
        print(f"✓ Created {file_path}")
    
    print(f"\n✅ Project '{project_name}' initialized at {project_path}")
    print("\nNext steps:")
    print(f"  cd {project_name}")
    print("  zig build")
    print("  zig build run")


def main():
    if len(sys.argv) < 2:
        print("Usage: python init_zig_project.py <project_name> [path]")
        sys.exit(1)
    
    project_name = sys.argv[1]
    path = sys.argv[2] if len(sys.argv) > 2 else "."
    
    init_project(project_name, path)


if __name__ == "__main__":
    main()
