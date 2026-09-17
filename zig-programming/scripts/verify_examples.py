#!/usr/bin/env python3
"""Compile and exercise the shipped Zig 0.16.0 examples in an isolated directory."""

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--zig", default="zig", help="Zig 0.16.0 executable")
    parser.add_argument("--io-only", action="store_true", help="Run streams and concurrency examples only")
    args = parser.parse_args()
    zig = shutil.which(args.zig)
    if zig is None:
        parser.error(f"Zig executable not found: {args.zig}")
    zig = str(Path(zig).resolve())
    version = subprocess.check_output([zig, "version"], text=True).strip()
    if version != "0.16.0":
        parser.error(f"Expected Zig 0.16.0, got {version}")
    source = Path(__file__).resolve().parents[1] / "examples"

    with tempfile.TemporaryDirectory(prefix="zig-skill-examples-") as temporary:
        work = Path(temporary)
        examples = work / "examples"
        shutil.copytree(source, examples)
        env = os.environ.copy()
        env["ZIG_GLOBAL_CACHE_DIR"] = str(work / "global-cache")
        env["ZIG_LOCAL_CACHE_DIR"] = str(work / "local-cache")

        def run(command, cwd=examples, expected=None, reject=None, show_output=True, timeout=180):
            print("+", " ".join(str(part) for part in command), flush=True)
            result = subprocess.run(command, cwd=cwd, env=env, text=True,
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout)
            if result.stdout and (show_output or result.returncode != 0):
                print(result.stdout, end="", flush=True)
            if reject is not None:
                if result.returncode == 0 or reject not in result.stdout:
                    raise RuntimeError("Expected compiler rejection was not observed")
            elif result.returncode != 0:
                raise subprocess.CalledProcessError(result.returncode, command)
            if expected is not None and expected not in result.stdout:
                raise RuntimeError(f"Missing expected output: {expected!r}")

        run([zig, "fmt", "--check", "."])
        # Compile separately so a timeout kills the test binary and all its threads,
        # rather than killing a compiler driver with a test subprocess still alive.
        for mode in ("Debug", "ReleaseSafe", "ReleaseFast"):
            for name in ("concurrency.zig", "batch-runner.zig", "streams.zig"):
                suffix = ".exe" if os.name == "nt" else ""
                binary = work / (Path(name).stem + "-" + mode + suffix)
                run([zig, "test", name, f"-O{mode}", "--test-no-exec", f"-femit-bin={binary}"])
                run([str(binary)], timeout=30)
        if args.io_only:
            print("All streams and concurrency checks passed. Threaded and inline backends tested; no throughput claim.")
            return
        for mode in ("Debug", "ReleaseSafe", "ReleaseFast"):
            for name in ("ownership.zig", "comptime.zig", "simd.zig", "binary.zig"):
                run([zig, "test", name, f"-O{mode}"])
        run([zig, "test", "invalid-comptime.zig"], reject="Buffer capacity must be positive")
        run([zig, "run", "runtime.zig"], expected="runtime checks passed")
        project = examples / "project"
        run([zig, "build", "--help"], cwd=project, expected="check", show_output=False)
        run([zig, "build", "test", "--summary", "all"], cwd=project, expected="1/1 tests passed")
        run([zig, "build", "--prefix", str(work / "install")], cwd=project)
        binary = work / "install" / "bin" / ("sample.exe" if os.name == "nt" else "sample")
        run([str(binary)], cwd=project, expected="generated fixture")
        run([zig, "build", "run"], cwd=project, expected="generated fixture")
        # A changed declared input must update what the executable embeds.
        (project / "message.txt").write_text("updated fixture\n")
        run([zig, "build", "run"], cwd=project, expected="updated fixture")
        run([zig, "build", "run"], cwd=project, expected="updated fixture")
        run([zig, "build", "check", "-Dtarget=x86_64-linux-musl", "-Doptimize=ReleaseSafe"], cwd=project)
        print("All example checks passed. HTTP compiled only; Linux cross-compiled only.")


if __name__ == "__main__":
    main()
