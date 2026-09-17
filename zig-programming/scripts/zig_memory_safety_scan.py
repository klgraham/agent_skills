#!/usr/bin/env python3
"""Heuristic Zig memory-safety risk inventory.

This scanner finds review candidates. It does not prove that a bug exists.
It deliberately uses only the Python standard library so it can run in an
arbitrary Zig repository without installing dependencies.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


EXCLUDED_PARTS = {
    ".git",
    ".zig-cache",
    "zig-cache",
    "zig-out",
    "node_modules",
    "vendor",
    "third_party",
}

SEVERITY_RANK = {
    "inventory": 0,
    "low": 1,
    "medium": 2,
    "high": 3,
    "critical": 4,
}


@dataclass(frozen=True)
class Finding:
    rule_id: str
    category: str
    severity: str
    confidence: str
    path: str
    line: int
    message: str
    evidence: str


@dataclass(frozen=True)
class Rule:
    rule_id: str
    category: str
    severity: str
    confidence: str
    pattern: re.Pattern[str]
    message: str


RULES = (
    Rule(
        "ZMS001",
        "pointer-conversion",
        "medium",
        "high",
        re.compile(r"@(ptrCast|intFromPtr|ptrFromInt|fieldParentPtr)\b"),
        "Unsafe pointer conversion or reconstruction requires a local validity proof.",
    ),
    Rule(
        "ZMS002",
        "pointer-conversion",
        "medium",
        "high",
        re.compile(r"@alignCast\b"),
        "Alignment cast requires proof that the source address meets the target alignment.",
    ),
    Rule(
        "ZMS003",
        "aliasing",
        "medium",
        "high",
        re.compile(r"@constCast\b"),
        "Const removal requires proof that mutation is permitted and aliases remain valid.",
    ),
    Rule(
        "ZMS004",
        "pointer-representation",
        "medium",
        "high",
        re.compile(r"\ballowzero\b"),
        "allowzero admits address zero into a non-optional pointer contract.",
    ),
    Rule(
        "ZMS005",
        "pointer-representation",
        "inventory",
        "high",
        re.compile(r"\[(?:\*c|\*)(?::[^\]]+)?\]"),
        "Many-item or C pointer has no native length; trace the external bounds contract.",
    ),
    Rule(
        "ZMS006",
        "initialization",
        "inventory",
        "high",
        re.compile(r"\bundefined\b"),
        "Explicit undefined value requires proof that every read follows initialization.",
    ),
    Rule(
        "ZMS007",
        "allocation",
        "inventory",
        "medium",
        re.compile(r"\.(?:alloc|create|dupe|dupeZ|realloc|allocSentinel)\s*\("),
        "Allocation or reallocation site: identify owner, allocator, failure cleanup, and invalidated aliases.",
    ),
    Rule(
        "ZMS008",
        "cleanup",
        "inventory",
        "medium",
        re.compile(r"\.(?:free|destroy|deinit)\s*\("),
        "Cleanup site: verify allocator pairing, exactly-once authority, and absence of live aliases.",
    ),
    Rule(
        "ZMS009",
        "pointer-invalidation",
        "inventory",
        "high",
        re.compile(
            r"\.(?:append|appendSlice|insert|resize|ensureTotalCapacity|"
            r"ensureUnusedCapacity|shrinkAndFree|clearAndFree|orderedRemove|"
            r"swapRemove|put|putNoClobber|fetchPut|remove)\s*\("
        ),
        "Container mutation may reallocate, rehash, reorder, or remove storage; check outstanding views.",
    ),
    Rule(
        "ZMS010",
        "pointer-invalidation",
        "inventory",
        "high",
        re.compile(r"\.items(?:\s*\[|\b)"),
        "Collection items view or interior access: determine which later operations invalidate it.",
    ),
    Rule(
        "ZMS011",
        "arena-lifetime",
        "medium",
        "medium",
        re.compile(
            r"\b[A-Za-z_]\w*(?:arena|pool|scratch)\w*\."
            r"(?:reset|deinit)\s*\(",
            re.IGNORECASE,
        ),
        "Arena/pool bulk lifetime boundary; all derived borrows may become invalid.",
    ),
    Rule(
        "ZMS012",
        "concurrency",
        "medium",
        "high",
        re.compile(r"\bstd\.Thread\.(?:spawn|Pool)|\bThread\.spawn\b"),
        "Thread boundary: prove capture lifetime, ownership transfer, shutdown ordering, and allocator safety.",
    ),
    Rule(
        "ZMS013",
        "concurrency",
        "inventory",
        "high",
        re.compile(r"\b(?:Mutex|RwLock|Condition|Semaphore|WaitGroup)\b"),
        "Synchronization primitive: identify exactly which state it protects and verify all access paths.",
    ),
    Rule(
        "ZMS014",
        "concurrency",
        "medium",
        "high",
        re.compile(r"\bstd\.atomic\b|@atomic(?:Load|Store|Rmw)\b|@cmpxchg(?:Strong|Weak)\b"),
        "Atomic operation requires a memory-ordering argument and, for pointers, a reclamation protocol.",
    ),
    Rule(
        "ZMS015",
        "concurrency",
        "low",
        "high",
        re.compile(r"\bvolatile\b"),
        "volatile is not synchronization; verify it is used only for externally changing memory such as MMIO.",
    ),
    Rule(
        "ZMS016",
        "aliasing",
        "inventory",
        "high",
        re.compile(r"\bnoalias\b"),
        "noalias is a caller contract; verify no call passes overlapping storage.",
    ),
    Rule(
        "ZMS017",
        "allocator-domain",
        "low",
        "high",
        re.compile(r"\bstd\.heap\.(?:page_allocator|c_allocator)\b"),
        "Global allocator bypass: verify this lifetime/accounting domain is intentional and documented.",
    ),
)

FIELD_PATTERN = re.compile(
    r"^\s*[A-Za-z_]\w*\s*:\s*(?:\?\s*)?(?:\[\]|\*)[^=]*,\s*(?://.*)?$"
)
FUNCTION_BORROW_RETURN = re.compile(
    r"\b(?:pub\s+)?fn\s+[A-Za-z_]\w*\s*\([^)]*\)\s*(?:![ \t]*)?"
    r"(?:\?\s*)?(?:\[\]|\*)"
)
DEINIT_RECEIVER = re.compile(
    r"\bfn\s+deinit\s*\(\s*(?:self|[A-Za-z_]\w*)\s*:\s*([^,)]+)"
)
TOP_LEVEL_VAR = re.compile(r"^\s*(?:pub\s+)?(?:threadlocal\s+)?var\s+")


def iter_zig_files(root: Path) -> Iterable[Path]:
    if root.is_file():
        if root.suffix == ".zig":
            yield root
        return

    for path in sorted(root.rglob("*.zig")):
        try:
            relative_parts = path.relative_to(root).parts
        except ValueError:
            relative_parts = path.parts
        if any(part in EXCLUDED_PARTS for part in relative_parts):
            continue
        yield path


def display_path(path: Path, root: Path) -> str:
    base = root if root.is_dir() else root.parent
    try:
        return str(path.relative_to(base))
    except ValueError:
        return str(path)


def evidence_text(line: str) -> str:
    compact = " ".join(line.strip().split())
    return compact[:237] + "..." if len(compact) > 240 else compact


def add_finding(
    findings: list[Finding],
    seen: set[tuple[str, str, int]],
    *,
    rule_id: str,
    category: str,
    severity: str,
    confidence: str,
    path: str,
    line_number: int,
    message: str,
    evidence: str,
) -> None:
    key = (rule_id, path, line_number)
    if key in seen:
        return
    seen.add(key)
    findings.append(
        Finding(
            rule_id=rule_id,
            category=category,
            severity=severity,
            confidence=confidence,
            path=path,
            line=line_number,
            message=message,
            evidence=evidence_text(evidence),
        )
    )


def scan_file(path: Path, root: Path) -> list[Finding]:
    findings: list[Finding] = []
    seen: set[tuple[str, str, int]] = set()
    relative_path = display_path(path, root)

    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        return [
            Finding(
                rule_id="ZMS000",
                category="scanner",
                severity="low",
                confidence="high",
                path=relative_path,
                line=0,
                message=f"Could not read file: {exc}",
                evidence="",
            )
        ]

    brace_depth = 0
    for line_number, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("//"):
            continue

        code = line.split("//", 1)[0]

        if brace_depth == 0 and TOP_LEVEL_VAR.search(code):
            add_finding(
                findings,
                seen,
                rule_id="ZMS018",
                category="concurrency",
                severity="medium",
                confidence="medium",
                path=relative_path,
                line_number=line_number,
                message="Mutable top-level state may be shared across threads; establish confinement or synchronization.",
                evidence=line,
            )

        if FIELD_PATTERN.search(code):
            add_finding(
                findings,
                seen,
                rule_id="ZMS019",
                category="ownership-contract",
                severity="inventory",
                confidence="medium",
                path=relative_path,
                line_number=line_number,
                message="Pointer/slice field needs an explicit owned, borrowed, shared, handle, or static contract.",
                evidence=line,
            )

        if FUNCTION_BORROW_RETURN.search(code):
            add_finding(
                findings,
                seen,
                rule_id="ZMS020",
                category="borrow-boundary",
                severity="inventory",
                confidence="medium",
                path=relative_path,
                line_number=line_number,
                message="Function returns a pointer or slice; document owner, validity interval, and invalidators.",
                evidence=line,
            )

        deinit_match = DEINIT_RECEIVER.search(code)
        if deinit_match and not deinit_match.group(1).strip().startswith("*"):
            add_finding(
                findings,
                seen,
                rule_id="ZMS021",
                category="single-owner",
                severity="medium",
                confidence="high",
                path=relative_path,
                line_number=line_number,
                message="deinit receiver is passed by value; cleanup cannot invalidate the caller's owner value.",
                evidence=line,
            )

        for rule in RULES:
            if rule.pattern.search(code):
                add_finding(
                    findings,
                    seen,
                    rule_id=rule.rule_id,
                    category=rule.category,
                    severity=rule.severity,
                    confidence=rule.confidence,
                    path=relative_path,
                    line_number=line_number,
                    message=rule.message,
                    evidence=line,
                )

        # Approximation used only to distinguish likely top-level `var` declarations.
        # Braces in multiline strings can reduce confidence but do not affect other rules.
        brace_depth = max(0, brace_depth + code.count("{") - code.count("}"))

    return findings


def scan(root: Path) -> tuple[list[Finding], int]:
    files = list(iter_zig_files(root))
    findings: list[Finding] = []
    for path in files:
        findings.extend(scan_file(path, root))

    findings.sort(
        key=lambda item: (
            -SEVERITY_RANK[item.severity],
            item.path,
            item.line,
            item.rule_id,
        )
    )
    return findings, len(files)


def render_markdown(
    root: Path,
    findings: list[Finding],
    file_count: int,
    reported_findings: list[Finding] | None = None,
) -> str:
    reported = findings if reported_findings is None else reported_findings
    counts = Counter(item.severity for item in findings)
    categories = Counter(item.category for item in findings)
    output = [
        "# Zig memory-safety scan",
        "",
        f"- Root: `{root}`",
        f"- Zig files scanned: {file_count}",
        f"- Total candidates: {len(findings)}",
        f"- Reported candidates: {len(reported)}",
        "- Interpretation: heuristic review inventory, not confirmed defects",
        "",
        "## Severity summary",
        "",
    ]

    for severity in ("critical", "high", "medium", "low", "inventory"):
        output.append(f"- {severity}: {counts.get(severity, 0)}")

    output.extend(["", "## Category summary", ""])
    for category, count in sorted(categories.items()):
        output.append(f"- {category}: {count}")

    output.extend(["", "## Candidates", ""])
    if not reported:
        output.append("No candidates matched the reporting threshold. This is not proof of memory safety.")
        return "\n".join(output)

    current_severity = None
    for item in reported:
        if item.severity != current_severity:
            if current_severity is not None:
                output.append("")
            current_severity = item.severity
            output.extend([f"### {current_severity.title()}", ""])
        output.append(
            f"- **{item.rule_id}** `{item.path}:{item.line}` "
            f"[{item.category}; confidence={item.confidence}] — {item.message}"
        )
        if item.evidence:
            sanitized_evidence = item.evidence.replace("`", "'")
            output.append(f"  - Evidence: `{sanitized_evidence}`")

    output.extend(
        [
            "",
            "## Required next step",
            "",
            "Trace each important candidate to its symbol definition, callers, owner, invalidators, and cleanup path. "
            "Report only source-verified reachable defects as findings.",
        ]
    )
    return "\n".join(output)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Inventory Zig memory-safety review candidates without claiming proof."
    )
    parser.add_argument("root", nargs="?", default=".", help="Zig file or repository root")
    parser.add_argument(
        "--format",
        choices=("markdown", "json"),
        default="markdown",
        help="Output format",
    )
    parser.add_argument(
        "--min-severity",
        choices=("inventory", "low", "medium", "high", "critical"),
        default="inventory",
        help="Report only candidates at or above this severity while retaining full summary counts",
    )
    parser.add_argument(
        "--fail-on",
        choices=("none", "inventory", "low", "medium", "high", "critical"),
        default="none",
        help="Exit 1 when a candidate at or above this severity is present",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    root = Path(args.root).expanduser().resolve()
    if not root.exists():
        print(f"error: path does not exist: {root}", file=sys.stderr)
        return 2

    findings, file_count = scan(root)
    minimum_rank = SEVERITY_RANK[args.min_severity]
    reported_findings = [
        item for item in findings if SEVERITY_RANK[item.severity] >= minimum_rank
    ]
    if args.format == "json":
        print(
            json.dumps(
                {
                    "root": str(root),
                    "zig_files_scanned": file_count,
                    "candidate_count": len(findings),
                    "reported_candidate_count": len(reported_findings),
                    "min_severity": args.min_severity,
                    "is_proof": False,
                    "findings": [asdict(item) for item in reported_findings],
                },
                indent=2,
                sort_keys=True,
            )
        )
    else:
        print(render_markdown(root, findings, file_count, reported_findings))

    if args.fail_on != "none":
        threshold = SEVERITY_RANK[args.fail_on]
        if any(SEVERITY_RANK[item.severity] >= threshold for item in findings):
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
