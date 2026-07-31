#!/usr/bin/env python3
"""Static regression checks for the Jarvis Codex harness contract."""

from __future__ import annotations

import json
import sys
import tomllib
from pathlib import Path


ROOT = Path(__file__).parents[1]
REQUIRED_SKILLS = {
    "project-planning",
    "grounded-research",
    "independent-review",
    "document-delivery",
    "verify-change",
}
REQUIRED_AGENTS = {
    "jarvis_explorer",
    "jarvis_reviewer",
    "jarvis_builder",
}


def fail(message: str) -> None:
    raise AssertionError(message)


def validate_manifest() -> None:
    manifest = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text())
    if manifest["name"] != "jarvis-codex":
        fail("manifest name must be jarvis-codex")
    if manifest.get("skills") != "./skills/":
        fail("manifest must package ./skills/")


def validate_skills() -> None:
    found = {path.parent.name for path in (ROOT / "skills").glob("*/SKILL.md")}
    if found != REQUIRED_SKILLS:
        fail(f"skill set mismatch: {sorted(found)}")
    for skill in REQUIRED_SKILLS:
        text = (ROOT / "skills" / skill / "SKILL.md").read_text()
        if "[TODO" in text or "TODO:" in text:
            fail(f"placeholder remains in {skill}")
        if len(text.splitlines()) > 500:
            fail(f"{skill} exceeds the 500-line skill budget")


def validate_agents() -> None:
    found: set[str] = set()
    for path in (ROOT / ".codex" / "agents").glob("*.toml"):
        data = tomllib.loads(path.read_text())
        for field in ("name", "description", "developer_instructions"):
            if not data.get(field):
                fail(f"{path}: missing {field}")
        if "model" in data:
            fail(f"{path}: model must inherit instead of being pinned")
        found.add(data["name"])
    if found != REQUIRED_AGENTS:
        fail(f"agent set mismatch: {sorted(found)}")


def validate_core_contract() -> None:
    text = (ROOT / "AGENTS.md").read_text()
    required_phrases = (
        "before changing code",
        "verification",
        "delegate only",
        "external actions",
        "compact envelope",
    )
    for phrase in required_phrases:
        if phrase not in text.lower():
            fail(f"AGENTS.md missing contract phrase: {phrase}")
    if len(text.splitlines()) > 250:
        fail("AGENTS.md exceeds the 250-line core budget")


def validate_routing_fixture_schema() -> None:
    payload = json.loads((ROOT / "evals" / "routing-cases.json").read_text())
    cases = payload.get("cases", [])
    ids = [case["id"] for case in cases]
    if len(cases) < 12:
        fail("routing suite needs at least 12 cases")
    if len(ids) != len(set(ids)):
        fail("routing case IDs must be unique")
    allowed_routes = {"direct", "standard", "gated"}
    allowed_skills = REQUIRED_SKILLS
    allowed_agents = REQUIRED_AGENTS
    expectation_fields = {
        "expected_route",
        "expected_skill",
        "expected_agents",
        "must_include",
        "must_not",
    }
    for case in cases:
        if not case.get("request"):
            fail(f"{case.get('id', '<missing>')}: request is required")
        if not expectation_fields.intersection(case):
            fail(f"{case['id']}: at least one expectation is required")
        if route := case.get("expected_route"):
            if route not in allowed_routes:
                fail(f"{case['id']}: invalid route {route}")
        if skill := case.get("expected_skill"):
            if skill not in allowed_skills:
                fail(f"{case['id']}: invalid skill {skill}")
        for agent in case.get("expected_agents", []):
            if agent not in allowed_agents:
                fail(f"{case['id']}: invalid agent {agent}")
        for field in ("must_include", "must_not"):
            if field in case and not all(
                isinstance(value, str) and value.strip() for value in case[field]
            ):
                fail(f"{case['id']}: {field} must contain non-empty strings")


def main() -> int:
    checks = (
        validate_manifest,
        validate_skills,
        validate_agents,
        validate_core_contract,
        validate_routing_fixture_schema,
    )
    for check in checks:
        check()
        print(f"PASS {check.__name__}")
    print(f"PASS all {len(checks)} harness checks")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, KeyError, json.JSONDecodeError, tomllib.TOMLDecodeError) as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        raise SystemExit(1)
