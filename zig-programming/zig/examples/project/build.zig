const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const generator = b.addExecutable(.{
        .name = "fixture-generator",
        .root_module = b.createModule(.{
            .root_source_file = b.path("generate.zig"),
            .target = b.graph.host,
        }),
    });
    const generate = b.addRunArtifact(generator);
    generate.addFileArg(b.path("message.txt"));
    const message = generate.addOutputFileArg("message.txt");

    const core = b.addModule("sample", .{
        .root_source_file = b.path("src/root.zig"),
        .target = target,
        .optimize = optimize,
    });
    core.addIncludePath(b.path("include"));
    core.addCSourceFile(.{ .file = b.path("src/helper.c"), .flags = &.{"-std=c11"} });
    const exe = b.addExecutable(.{
        .name = "sample",
        .root_module = b.createModule(.{
            .root_source_file = b.path("src/main.zig"),
            .target = target,
            .optimize = optimize,
            .imports = &.{.{ .name = "sample", .module = core }},
        }),
    });
    exe.root_module.addAnonymousImport("message", .{ .root_source_file = message });
    b.installArtifact(exe);
    const run = b.addRunArtifact(exe);
    if (b.args) |args| run.addArgs(args);
    b.step("run", "Run the sample").dependOn(&run.step);
    const tests = b.addTest(.{ .root_module = core });
    b.step("test", "Run native tests").dependOn(&b.addRunArtifact(tests).step);
    const check = b.step("check", "Compile application and tests without executing them");
    check.dependOn(&exe.step);
    check.dependOn(&tests.step);
}
