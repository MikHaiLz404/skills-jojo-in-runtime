#!/usr/bin/env python3
"""Validate that a Claude marketplace distributes Emily-owned plugins only."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Sequence


BLOCKED_ROOTS = {"external", "caveman", "understand-anything"}


def load_json(path: Path, errors: list[str]) -> object | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"missing JSON file: {path}")
    except json.JSONDecodeError as error:
        errors.append(f"invalid JSON in {path}: {error.msg}")
    return None


def validate_plugin(root: Path, plugin: object) -> tuple[str | None, list[str]]:
    errors: list[str] = []
    if not isinstance(plugin, dict):
        return None, ["plugin entry must be an object"]

    name = plugin.get("name")
    source = plugin.get("source")
    if not isinstance(name, str) or not name:
        errors.append("plugin entry has no valid name")
        return None, errors
    if not name.startswith("emily-"):
        errors.append(f"{name}: plugin name must start with emily-")
    if not isinstance(source, str) or not source.startswith("./"):
        errors.append(f"{name}: source must be a repository-relative ./ path")
        return name, errors

    source_path = Path(source[2:])
    if not source_path.parts:
        errors.append(f"{name}: source must name a plugin directory")
        return name, errors
    if source_path.parts[0] in BLOCKED_ROOTS:
        errors.append(f"{name}: source cannot use external root {source_path.parts[0]}")
        return name, errors

    package = (root / source_path).resolve()
    try:
        package.relative_to(root)
    except ValueError:
        errors.append(f"{name}: source escapes repository root")
        return name, errors
    if not package.is_dir():
        errors.append(f"{name}: source directory is missing: {source}")
        return name, errors
    if (package / ".git").exists():
        errors.append(f"{name}: source contains a nested Git directory")
    if not (package / ".claude-plugin" / "plugin.json").is_file():
        errors.append(f"{name}: source is missing .claude-plugin/plugin.json")
    return name, errors


def main(argv: Sequence[str]) -> int:
    root = Path(argv[1] if len(argv) > 1 else ".").resolve()
    errors: list[str] = []
    manifest = load_json(root / ".claude-plugin" / "marketplace.json", errors)
    if not isinstance(manifest, dict):
        errors.append("marketplace manifest must be a JSON object")
    else:
        plugins = manifest.get("plugins")
        if not isinstance(plugins, list):
            errors.append("marketplace manifest plugins must be a list")
            plugins = []
        for plugin in plugins:
            _, plugin_errors = validate_plugin(root, plugin)
            errors.extend(plugin_errors)

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    for plugin in manifest["plugins"]:
        print(f"verified {plugin['name']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
