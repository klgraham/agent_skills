#!/usr/bin/env python3
"""Read saved Annotated Equations installation and enablement for one Obsidian vault."""

import argparse
import json
from pathlib import Path

PLUGIN_ID = "annotated-equations"
PLUGIN_FILES = ("manifest.json", "main.js", "styles.css")


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def inspect(vault, config_dir=".obsidian"):
    config = vault / config_dir
    result = {
        "config_dir": str(config),
        "install": "unknown",
        "enabled_in_config": None,
        "version": None,
        "min_app_version": None,
        "issues": [],
    }
    if not vault.is_dir() or not config.is_dir():
        result["issues"].append("Vault or configuration folder unavailable; check the vault and its active config folder.")
        return result

    enabled_path = config / "community-plugins.json"
    try:
        enabled = read_json(enabled_path)
        if not isinstance(enabled, list) or not all(isinstance(x, str) for x in enabled):
            raise ValueError("expected a list of plugin IDs")
        result["enabled_in_config"] = PLUGIN_ID in enabled
    except FileNotFoundError:
        result["issues"].append("No saved community plugin list; enablement is unverified.")
    except (ValueError, OSError):
        result["issues"].append("Cannot read the saved community plugin list.")

    folder = config / "plugins" / PLUGIN_ID
    try:
        folder.stat()
    except FileNotFoundError:
        result["install"] = "missing"
        return result
    except OSError:
        result["issues"].append("Cannot access the plugin folder.")
        return result

    try:
        missing = [name for name in PLUGIN_FILES if (folder / name).stat().st_size == 0
                   or not (folder / name).is_file()]
        manifest = read_json(folder / "manifest.json")
        if missing or not isinstance(manifest, dict) or manifest.get("id") != PLUGIN_ID:
            raise ValueError("expected a matching manifest and nonempty release files")
        for field, key in (("version", "version"), ("minAppVersion", "min_app_version")):
            if not isinstance(manifest.get(field), str) or not manifest[field].strip():
                raise ValueError("expected version and minimum app version")
            result[key] = manifest[field]
        result["install"] = "installed"
    except (FileNotFoundError, ValueError, NotADirectoryError):
        result["install"] = "incomplete"
        result["issues"].append("Plugin folder is present but its manifest or release files are missing or invalid.")
    except OSError:
        result["issues"].append("Cannot read the plugin manifest or release files.")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("vault", type=Path, help="Path to the intended vault root")
    parser.add_argument("--config-dir", type=Path, default=Path(".obsidian"),
                        help="Active configuration folder relative to the vault root")
    args = parser.parse_args()
    if args.config_dir.is_absolute() or ".." in args.config_dir.parts or args.config_dir == Path("."):
        parser.error("--config-dir must be a subdirectory relative to the vault root")
    print(json.dumps(inspect(args.vault.expanduser(), args.config_dir), indent=2))


if __name__ == "__main__":
    main()
