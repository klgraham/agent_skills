#!/usr/bin/env python3
"""Regression tests for the heuristic memory-safety scanner."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from zig_memory_safety_scan import render_markdown, scan  # noqa: E402


class ScannerRegressionTests(unittest.TestCase):
    def test_inventory_and_markdown_are_explicitly_heuristic(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "sample.zig").write_text(
                """
const std = @import(\"std\");

pub fn example(allocator: std.mem.Allocator) !void {
    const bytes = try allocator.alloc(u8, 8);
    defer allocator.free(bytes);
    _ = @alignCast(bytes.ptr);
}
""".strip()
                + "\n",
                encoding="utf-8",
            )

            findings, file_count = scan(root)
            self.assertEqual(file_count, 1)
            self.assertIn("ZMS002", {finding.rule_id for finding in findings})

            report = render_markdown(root, findings, file_count)
            self.assertIn("heuristic review inventory, not confirmed defects", report)
            self.assertIn("Trace each important candidate", report)


if __name__ == "__main__":
    unittest.main()
