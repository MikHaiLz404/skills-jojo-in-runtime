#!/usr/bin/env python3
"""Validate that a Claude marketplace distributes Emily-owned plugins only."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Sequence


BLOCKED_ROOTS = {"external", "caveman", "understand-anything"}
KNOWN_EXTERNAL = {
    "caveman",
    "understand-anything",
    "character-sheet-pipeline",
    "character-sheet-pipeline-openai",
}
SOURCE_FIELDS = {
    "name",
    "classification",
    "upstream",
    "attribution",
    "license_or_status",
    "update",
    "local_checkout",
}


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


def validate_external_registry(root: Path) -> list[str]:
    registry_path = root / "external" / "sources.json"
    if not registry_path.exists():
        return []

    errors: list[str] = []
    registry = load_json(registry_path, errors)
    if not isinstance(registry, dict):
        return errors + ["external registry must be a JSON object"]
    sources = registry.get("sources")
    if not isinstance(sources, list):
        return errors + ["external registry sources must be a list"]

    names: set[str] = set()
    for source in sources:
        if not isinstance(source, dict):
            errors.append("external registry source must be an object")
            continue
        name = source.get("name")
        label = name if isinstance(name, str) and name else "unnamed source"
        for field in SOURCE_FIELDS:
            if not isinstance(source.get(field), str) or not source[field]:
                errors.append(f"{label}: external registry requires {field}")
        classification = source.get("classification")
        if classification not in {"external", "unverified", "first-party"}:
            errors.append(f"{label}: invalid classification {classification!r}")
        if isinstance(name, str):
            if name in names:
                errors.append(f"{name}: duplicate external registry source")
            names.add(name)
        local_checkout = source.get("local_checkout")
        if isinstance(local_checkout, str) and not local_checkout.startswith(
            "external/checkouts/"
        ):
            errors.append(f"{label}: local_checkout must be below external/checkouts/")
        if classification in {"external", "unverified"} and source.get("marketplace") is not False:
            errors.append(f"{label}: {classification} source must set marketplace to false")
        if classification == "first-party":
            target_plugin = source.get("target_plugin")
            if not isinstance(target_plugin, str) or not target_plugin.startswith("emily-"):
                errors.append(f"{label}: first-party source requires an emily-* target_plugin")

    for name in sorted(KNOWN_EXTERNAL - names):
        errors.append(f"external registry is missing known source: {name}")
    for name in sorted(KNOWN_EXTERNAL & names):
        source = next(item for item in sources if item.get("name") == name)
        if source.get("classification") != "external":
            errors.append(f"{name}: known external source must classify as external")
        if source.get("marketplace") is not False:
            errors.append(f"{name}: known external source must set marketplace to false")
    return errors


def discover_skill_packages(root: Path) -> dict[str, set[str]]:
    discovered: dict[str, set[str]] = {}
    for package in root.glob("emily-*"):
        skills = package / "skills"
        if not skills.is_dir():
            continue
        for skill in skills.iterdir():
            if (skill / "SKILL.md").is_file():
                discovered.setdefault(skill.name, set()).add(package.name)
    return discovered


def validate_provenance_imports(root: Path) -> list[str]:
    registry_path = root / "external" / "sources.json"
    if not registry_path.exists():
        return []
    errors: list[str] = []
    registry = load_json(registry_path, errors)
    if not isinstance(registry, dict) or not isinstance(registry.get("sources"), list):
        return errors

    discovered = discover_skill_packages(root)
    for source in registry["sources"]:
        if not isinstance(source, dict):
            continue
        name = source.get("name")
        classification = source.get("classification")
        if not isinstance(name, str) or not isinstance(classification, str):
            continue
        locations = discovered.get(name, set())
        if classification == "first-party":
            target = source.get("target_plugin")
            if not isinstance(target, str):
                continue
            if locations != {target}:
                rendered_locations = ", ".join(sorted(locations)) or "not imported"
                errors.append(
                    f"{name}: first-party source must appear once in {target}, found {rendered_locations}"
                )
        elif classification in {"external", "unverified"} and locations:
            errors.append(
                f"{name}: {classification} source must not appear in Emily packages ({', '.join(sorted(locations))})"
            )
    return errors


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
        errors.extend(validate_external_registry(root))
        errors.extend(validate_provenance_imports(root))

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    for plugin in manifest["plugins"]:
        print(f"verified {plugin['name']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
