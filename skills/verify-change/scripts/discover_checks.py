#!/usr/bin/env python3
"""Discover likely repository validation commands without executing them."""

from __future__ import annotations

import json
import sys
from pathlib import Path


SCRIPT_NAMES = (
    "test",
    "test:unit",
    "test:integration",
    "test:e2e",
    "lint",
    "typecheck",
    "check",
    "build",
    "validate",
)


def relative_dir(root: Path, path: Path) -> str:
    relative = path.relative_to(root)
    return "." if relative == Path(".") else str(relative)


def add(
    results: list[dict[str, str]],
    source: Path,
    command: str,
    cwd: str,
) -> None:
    item = {"source": str(source), "cwd": cwd, "command": command}
    if item not in results:
        results.append(item)


def discover(root: Path) -> list[dict[str, str]]:
    results: list[dict[str, str]] = []

    for package_json in root.rglob("package.json"):
        if any(part in {"node_modules", ".git", "dist", "build"} for part in package_json.parts):
            continue
        try:
            scripts = json.loads(package_json.read_text(encoding="utf-8")).get("scripts", {})
        except (OSError, json.JSONDecodeError):
            continue
        prefix = "npm run"
        for name in SCRIPT_NAMES:
            if name in scripts:
                add(
                    results,
                    package_json.relative_to(root),
                    f"{prefix} {name}",
                    relative_dir(root, package_json.parent),
                )

    candidates = {
        "Makefile": ("make test", "make lint", "make check"),
        "pyproject.toml": ("pytest", "ruff check .", "mypy ."),
        "tox.ini": ("tox",),
        "Cargo.toml": ("cargo test", "cargo clippy --all-targets --all-features"),
        "go.mod": ("go test ./...", "go vet ./..."),
        "gradlew": ("./gradlew test",),
        "mvnw": ("./mvnw test",),
    }
    for filename, commands in candidates.items():
        for path in root.rglob(filename):
            if ".git" in path.parts:
                continue
            for command in commands:
                add(
                    results,
                    path.relative_to(root),
                    command,
                    relative_dir(root, path.parent),
                )

    for workflow_dir in (root / ".github" / "workflows", root / ".gitlab"):
        if workflow_dir.exists():
            add(
                results,
                workflow_dir.relative_to(root),
                "Inspect CI workflow for canonical checks",
                ".",
            )

    return results


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    if not root.is_dir():
        print(json.dumps({"error": f"not a directory: {root}"}, ensure_ascii=False))
        return 2
    print(json.dumps({"root": str(root), "checks": discover(root)}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
