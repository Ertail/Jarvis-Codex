#!/usr/bin/env python3
"""List, resolve, validate, clone, and activate document design systems."""

from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
BUILTIN_REGISTRY_DIR = SKILL_DIR / "assets" / "design-systems"
DEFAULT_ACTIVE_FILE = SKILL_DIR / "active.txt"
USER_ROOT = Path(
    os.environ.get(
        "JARVIS_DOC_STYLE_HOME",
        Path.home() / ".codex" / "jarvis-codex" / "doc-style",
    )
).expanduser()
USER_REGISTRY_DIR = USER_ROOT / "design-systems"
USER_ACTIVE_FILE = USER_ROOT / "active.txt"
REQUIRED_FILES = (
    "design-system.css",
    "components.md",
    "template.html",
    "preview.html",
)
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def validate_name(name: str) -> None:
    if not NAME_RE.fullmatch(name):
        raise ValueError(
            f"invalid style name {name!r}; use lowercase hyphen-case"
        )


def registered_styles() -> list[str]:
    names: set[str] = set()
    for registry in (BUILTIN_REGISTRY_DIR, USER_REGISTRY_DIR):
        if registry.is_dir():
            names.update(path.name for path in registry.iterdir() if path.is_dir())
    return sorted(names)


def style_dir(name: str) -> Path:
    validate_name(name)
    user_style = USER_REGISTRY_DIR / name
    if user_style.is_dir():
        return user_style
    return BUILTIN_REGISTRY_DIR / name


def read_active() -> str:
    pointer = USER_ACTIVE_FILE if USER_ACTIVE_FILE.is_file() else DEFAULT_ACTIVE_FILE
    if not pointer.is_file():
        raise ValueError(f"missing active style pointer: {pointer}")
    name = pointer.read_text(encoding="utf-8").strip()
    validate_name(name)
    return name


def extract_style(html: str, path: Path) -> str:
    match = re.search(r"<style>\s*(.*?)\s*</style>", html, flags=re.DOTALL)
    if not match:
        raise ValueError(f"{path}: missing <style> block")
    return match.group(1).strip()


def validate_style(name: str) -> list[str]:
    validate_name(name)
    target_dir = style_dir(name)
    errors: list[str] = []
    if not target_dir.is_dir():
        return [f"{name}: style directory does not exist"]

    for filename in REQUIRED_FILES:
        if not (target_dir / filename).is_file():
            errors.append(f"{name}: missing {filename}")
    if errors:
        return errors

    css = (target_dir / "design-system.css").read_text(
        encoding="utf-8"
    ).strip()
    for filename in ("template.html", "preview.html"):
        path = target_dir / filename
        try:
            embedded = extract_style(path.read_text(encoding="utf-8"), path)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        if embedded != css:
            errors.append(
                f"{name}: {filename} <style> differs from design-system.css"
            )

    required_markers = (
        "--paper:",
        "--ink:",
        "--ar:",
        "--arb:",
        "section.ch",
        ".tldr",
        ".tbl-wrap",
        "figure img",
        "max-width:100%",
    )
    for marker in required_markers:
        if marker not in css:
            errors.append(f"{name}: CSS missing contract marker {marker!r}")
    return errors


def print_errors(errors: list[str]) -> int:
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    return 1


def command_list() -> int:
    active = read_active()
    for name in registered_styles():
        source = "user" if (USER_REGISTRY_DIR / name).is_dir() else "builtin"
        print(f"{'*' if name == active else ' '} {name} [{source}]")
    return 0


def command_validate(name: str | None) -> int:
    names = [name] if name else registered_styles()
    if not names:
        print("no registered styles", file=sys.stderr)
        return 1
    errors = [error for item in names for error in validate_style(item)]
    if not name:
        try:
            active = read_active()
        except ValueError as exc:
            errors.append(str(exc))
        else:
            if active not in names:
                errors.append(f"active style {active!r} is not registered")
    if errors:
        return print_errors(errors)
    print(f"validated: {', '.join(names)}")
    return 0


def command_activate(name: str) -> int:
    errors = validate_style(name)
    if errors:
        return print_errors(errors)
    USER_ROOT.mkdir(parents=True, exist_ok=True)
    USER_ACTIVE_FILE.write_text(f"{name}\n", encoding="utf-8")
    print(name)
    return 0


def command_clone(name: str, source: str | None) -> int:
    validate_name(name)
    source = source or read_active()
    errors = validate_style(source)
    if errors:
        return print_errors(errors)
    if name in registered_styles():
        print(f"ERROR: style already exists: {name}", file=sys.stderr)
        return 1
    USER_REGISTRY_DIR.mkdir(parents=True, exist_ok=True)
    destination = USER_REGISTRY_DIR / name
    shutil.copytree(style_dir(source), destination)
    print(f"{source} -> {name}")
    return 0


def command_resolve(name: str | None) -> int:
    name = name or read_active()
    errors = validate_style(name)
    if errors:
        return print_errors(errors)
    print(style_dir(name))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("list")
    subparsers.add_parser("active")
    resolve = subparsers.add_parser("resolve")
    resolve.add_argument("name", nargs="?")
    validate = subparsers.add_parser("validate")
    validate.add_argument("name", nargs="?")
    activate = subparsers.add_parser("activate")
    activate.add_argument("name")
    clone = subparsers.add_parser("clone")
    clone.add_argument("name")
    clone.add_argument("--from", dest="source")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.command == "list":
            return command_list()
        if args.command == "active":
            print(read_active())
            return 0
        if args.command == "resolve":
            return command_resolve(args.name)
        if args.command == "validate":
            return command_validate(args.name)
        if args.command == "activate":
            return command_activate(args.name)
        if args.command == "clone":
            return command_clone(args.name, args.source)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    raise AssertionError(f"unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
