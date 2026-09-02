#!/usr/bin/env python3
"""Validate canonical skills and their Claude plugin distribution."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


FRONTMATTER_NAME = re.compile(r"^name:\s*['\"]?([^'\"\s]+)", re.MULTILINE)
MARKDOWN_LINK = re.compile(r"\[[^]]+\]\(([^)]+)\)")
DEFAULT_PROMPT = re.compile(r'^\s*default_prompt:\s*["\'](.*)["\']\s*$', re.MULTILINE)


def fail(message: str) -> None:
    raise ValueError(message)


def validate_markdown_links(skill_dir: Path) -> None:
    for source in skill_dir.rglob("*.md"):
        text = source.read_text(encoding="utf-8")
        for target in MARKDOWN_LINK.findall(text):
            if "://" in target or target.startswith("#"):
                continue
            path_text = target.split("#", 1)[0]
            local_target = (source.parent / path_text).resolve()
            if not local_target.exists():
                relative_source = source.relative_to(skill_dir)
                fail(f"{skill_dir.name}: {relative_source} has broken link {target}")


def validate_skill(repo: Path, skill_name: str) -> None:
    skill_dir = repo / skill_name
    entrypoint = skill_dir / "SKILL.md"
    if not entrypoint.is_file():
        fail(f"{skill_name}: missing SKILL.md")

    text = entrypoint.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        fail(f"{skill_name}: SKILL.md lacks YAML frontmatter")
    name = FRONTMATTER_NAME.search(text)
    if name is None or name.group(1) != skill_name:
        fail(f"{skill_name}: frontmatter name does not match directory")

    validate_markdown_links(skill_dir)

    metadata = skill_dir / "agents" / "openai.yaml"
    if not metadata.is_file():
        fail(f"{skill_name}: missing agents/openai.yaml")
    metadata_text = metadata.read_text(encoding="utf-8")
    default_prompt = DEFAULT_PROMPT.search(metadata_text)
    if default_prompt is None or f"${skill_name}" not in default_prompt.group(1):
        fail(f"{skill_name}: default prompt must name ${skill_name}")


def validate_plugin(repo: Path, plugin_path: Path, skill_names: set[str]) -> None:
    plugin_dir = (repo / plugin_path).resolve()
    manifest_path = plugin_dir / ".claude-plugin" / "plugin.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("name") != plugin_dir.name:
        fail(f"{plugin_path}: manifest name does not match directory")

    links_dir = plugin_dir / "skills"
    linked_names = {path.name for path in links_dir.iterdir()}
    if linked_names != skill_names:
        fail(
            f"{plugin_path}: linked skills {sorted(linked_names)} do not match "
            f"expected {sorted(skill_names)}"
        )
    for name in linked_names:
        link = links_dir / name
        if not link.is_symlink():
            fail(f"{plugin_path}: skills/{name} is not a symlink")
        if link.resolve() != (repo / name).resolve():
            fail(f"{plugin_path}: skills/{name} resolves to the wrong target")

    marketplace_path = repo / ".claude-plugin" / "marketplace.json"
    marketplace = json.loads(marketplace_path.read_text(encoding="utf-8"))
    matches = [
        item
        for item in marketplace["plugins"]
        if item.get("name") == manifest["name"]
    ]
    expected_source = f"./{plugin_path.as_posix()}"
    if len(matches) != 1 or matches[0].get("source") != expected_source:
        fail(f"{plugin_path}: marketplace entry is missing or has the wrong source")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plugin", required=True, type=Path)
    parser.add_argument("skills", nargs="+")
    args = parser.parse_args()

    repo = Path(__file__).resolve().parent.parent
    for skill_name in args.skills:
        validate_skill(repo, skill_name)
    validate_plugin(repo, args.plugin, set(args.skills))
    print(
        f"validated {len(args.skills)} skills and plugin {args.plugin.as_posix()}"
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"validation failed: {error}", file=sys.stderr)
        sys.exit(1)
