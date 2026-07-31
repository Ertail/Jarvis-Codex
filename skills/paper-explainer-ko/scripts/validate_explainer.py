#!/usr/bin/env python3
"""Validate the structural and offline contract of a Korean paper explainer."""

from __future__ import annotations

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path


class ExplainerParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.lang = ""
        self.chapter_depth = 0
        self.chapter_tldrs: list[int] = []
        self.images: list[dict[str, str]] = []
        self.visual_ids: set[str] = set()
        self.svg_count = 0
        self.table_count = 0

    @staticmethod
    def classes(attrs: dict[str, str]) -> set[str]:
        return set(attrs.get("class", "").split())

    def handle_starttag(
        self, tag: str, raw_attrs: list[tuple[str, str | None]]
    ) -> None:
        attrs = {key: value or "" for key, value in raw_attrs}
        classes = self.classes(attrs)
        if tag == "html":
            self.lang = attrs.get("lang", "")
        if tag == "section" and "ch" in classes:
            self.chapter_depth += 1
            self.chapter_tldrs.append(0)
        elif self.chapter_depth and "tldr" in classes:
            self.chapter_tldrs[-1] += 1
        if tag == "img":
            self.images.append(attrs)
        elif tag == "svg":
            self.svg_count += 1
        elif tag == "table":
            self.table_count += 1
        if attrs.get("data-figure"):
            self.visual_ids.add(attrs["data-figure"].lower())

    def handle_endtag(self, tag: str) -> None:
        if tag == "section" and self.chapter_depth:
            self.chapter_depth -= 1


def extract_style(html: str, path: Path) -> str:
    match = re.search(r"<style>\s*(.*?)\s*</style>", html, flags=re.DOTALL)
    if not match:
        raise ValueError(f"{path}: missing <style> block")
    return match.group(1).strip()


def validate(
    html_path: Path, manifest_path: Path | None, template_path: Path | None
) -> list[str]:
    errors: list[str] = []
    html = html_path.read_text(encoding="utf-8")
    parser = ExplainerParser()
    parser.feed(html)

    if not parser.lang.lower().startswith("ko"):
        errors.append("root <html> must declare lang=\"ko\"")
    if not parser.chapter_tldrs:
        errors.append("no section.ch chapters found")
    for index, count in enumerate(parser.chapter_tldrs, start=1):
        if count == 0:
            errors.append(f"chapter {index} has no .tldr summary")
    for index, attrs in enumerate(parser.images, start=1):
        src = attrs.get("src", "")
        if not src.startswith("data:image/"):
            errors.append(f"image {index} is not an embedded data URI")

    if not (parser.images or parser.svg_count or parser.table_count):
        errors.append("document has no figure, table, or inline SVG visualization")

    if manifest_path:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        expected = {
            Path(item["file"]).stem.lower()
            for item in manifest
            if isinstance(item, dict) and item.get("file")
        }
        missing = sorted(expected - parser.visual_ids)
        if missing:
            errors.append(
                "manifest visuals missing from data-figure attributes: "
                + ", ".join(missing)
            )

    if template_path:
        try:
            output_style = extract_style(html, html_path)
            template_style = extract_style(
                template_path.read_text(encoding="utf-8"), template_path
            )
        except ValueError as exc:
            errors.append(str(exc))
        else:
            if output_style != template_style:
                errors.append("output <style> differs from the active template")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("html", type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--template", type=Path)
    args = parser.parse_args()

    try:
        errors = validate(args.html, args.manifest, args.template)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"validated: {args.html}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
