#!/usr/bin/env python3
"""Exercise the bundled PR Lens graph against the pinned CLI."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


CLI_PACKAGE = "@coldtea/pr-lens-cli@0.4.0"
SKILL_DIR = Path(__file__).resolve().parent.parent
EXAMPLE = SKILL_DIR / "references" / "example.graph.json"


def run(*args: str, expect_success: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["npx", "--yes", CLI_PACKAGE, *args],
        check=False,
        text=True,
        capture_output=True,
        timeout=120,
    )
    if expect_success and result.returncode != 0:
        sys.stderr.write(result.stdout)
        sys.stderr.write(result.stderr)
        raise RuntimeError(f"PR Lens failed: {' '.join(args)}")
    return result


def svg_hashes(output_dir: Path) -> dict[str, str]:
    assets = sorted(output_dir.glob("*.svg"))
    if not assets:
        raise RuntimeError("render produced no SVG files")

    hashes: dict[str, str] = {}
    for asset in assets:
        data = asset.read_bytes()
        text = data.decode("utf-8")
        if "<svg" not in text:
            raise RuntimeError(f"{asset.name} is not an SVG")
        if "<script" in text.lower():
            raise RuntimeError(f"{asset.name} contains a script element")
        hashes[asset.name] = hashlib.sha256(data).hexdigest()
    return hashes


def main() -> int:
    if shutil.which("npx") is None:
        raise RuntimeError("npx is required")

    with tempfile.TemporaryDirectory(prefix="pr-visualizer-") as raw_dir:
        work_dir = Path(raw_dir)
        graph = work_dir / "graph.json"
        output = work_dir / "rendered"
        shutil.copy2(EXAMPLE, graph)

        run("validate", str(graph))
        run("render", str(graph), "--out", str(output), "--theme", "both")

        manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
        drawn = json.loads((output / "drawn.graph.json").read_text(encoding="utf-8"))
        if drawn.get("schemaVersion") != "0.1.1":
            raise RuntimeError("drawn graph has the wrong schema version")
        if len(drawn.get("walkthrough", {}).get("steps", [])) < 2:
            raise RuntimeError("drawn graph has no usable walkthrough")
        assets = manifest.get("assets", [])
        if not assets:
            raise RuntimeError("render manifest has no assets")
        if {asset.get("theme") for asset in assets} != {"light", "dark"}:
            raise RuntimeError("render manifest does not contain both themes")
        for asset in assets:
            path = asset.get("path")
            if not isinstance(path, str) or not (output / path).is_file():
                raise RuntimeError("render manifest names a missing SVG")

        first_hashes = svg_hashes(output)
        run("render", str(graph), "--out", str(output), "--theme", "both")
        if first_hashes != svg_hashes(output):
            raise RuntimeError("the same graph did not render deterministically")

        broken = json.loads(graph.read_text(encoding="utf-8"))
        broken["edges"][0]["to"] = "node-that-does-not-exist"
        broken_path = work_dir / "broken.graph.json"
        broken_path.write_text(json.dumps(broken), encoding="utf-8")
        rejected = run("validate", str(broken_path), expect_success=False)
        if rejected.returncode == 0:
            raise RuntimeError("validator accepted a broken node reference")
        if "BROKEN_REFERENCE" not in rejected.stderr + rejected.stdout:
            raise RuntimeError("validator rejected the fixture for an unexpected reason")

        print(
            f"verified {len(first_hashes)} deterministic SVGs, "
            "a walkthrough, and broken-reference rejection"
        )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (
        OSError,
        RuntimeError,
        json.JSONDecodeError,
        subprocess.TimeoutExpired,
    ) as error:
        print(f"verification failed: {error}", file=sys.stderr)
        raise SystemExit(1)
