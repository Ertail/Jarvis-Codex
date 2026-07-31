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
        self.visual_tags: dict[str, str] = {}
        self.svg_count = 0
        self.table_count = 0
        self.tldr_depth = 0
        self.table_depth = 0
        self.source_sections: dict[str, dict[str, object]] = {}
        self.source_stack: list[str] = []
        self.paragraph_stack: list[set[str]] = []
        self.frames: list[tuple[str, bool, str | None]] = []

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
        opened_tldr = self.chapter_depth > 0 and "tldr" in classes
        if opened_tldr:
            self.chapter_tldrs[-1] += 1
            self.tldr_depth += 1
        source_id = attrs.get("data-source-section", "").strip()
        if source_id:
            if source_id in self.source_sections:
                self.source_sections[source_id]["duplicates"] = (
                    int(self.source_sections[source_id]["duplicates"]) + 1
                )
            else:
                self.source_sections[source_id] = {
                    "detail_text": [],
                    "paragraphs": 0,
                    "duplicates": 0,
                }
            self.source_stack.append(source_id)
        if tag not in {"area", "base", "br", "col", "embed", "hr", "img", "input",
                       "link", "meta", "param", "source", "track", "wbr"}:
            self.frames.append((tag, opened_tldr, source_id or None))
        if tag == "p":
            self.paragraph_stack.append(set(self.source_stack))
        if tag == "img":
            self.images.append(attrs)
        elif tag == "svg":
            self.svg_count += 1
        elif tag == "table":
            self.table_count += 1
            self.table_depth += 1
        if attrs.get("data-figure"):
            visual_id = attrs["data-figure"].lower()
            self.visual_ids.add(visual_id)
            self.visual_tags[visual_id] = tag

    def handle_endtag(self, tag: str) -> None:
        if tag == "section" and self.chapter_depth:
            self.chapter_depth -= 1
        if tag == "p" and self.paragraph_stack:
            for source_id in self.paragraph_stack.pop():
                self.source_sections[source_id]["paragraphs"] = (
                    int(self.source_sections[source_id]["paragraphs"]) + 1
                )
        if tag == "table" and self.table_depth:
            self.table_depth -= 1
        if self.frames:
            _, opened_tldr, source_id = self.frames.pop()
            if opened_tldr:
                self.tldr_depth -= 1
            if source_id:
                self.source_stack.pop()

    def handle_data(self, data: str) -> None:
        if not self.source_stack or self.tldr_depth or self.table_depth:
            return
        text = " ".join(data.split())
        if not text:
            return
        for source_id in self.source_stack:
            self.source_sections[source_id]["detail_text"].append(text)


def extract_style(html: str, path: Path) -> str:
    match = re.search(r"<style>\s*(.*?)\s*</style>", html, flags=re.DOTALL)
    if not match:
        raise ValueError(f"{path}: missing <style> block")
    return match.group(1).strip()


def validate(
    html_path: Path,
    manifest_path: Path | None,
    template_path: Path | None,
    coverage_path: Path | None = None,
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

    if coverage_path:
        coverage = json.loads(coverage_path.read_text(encoding="utf-8"))
        sections = coverage.get("sections", [])
        if not isinstance(sections, list) or not sections:
            errors.append("coverage file must contain a non-empty sections list")
        else:
            expected_ids: set[str] = set()
            for item in sections:
                if not isinstance(item, dict) or not str(item.get("id", "")).strip():
                    errors.append("each coverage section must have an id")
                    continue
                source_id = str(item["id"]).strip()
                expected_ids.add(source_id)
                actual = parser.source_sections.get(source_id)
                if actual is None:
                    errors.append(f"source section {source_id} is not represented")
                    continue
                if int(actual["duplicates"]):
                    errors.append(f"source section {source_id} is represented more than once")
                detail_chars = len("".join(actual["detail_text"]))
                min_chars = int(item.get("min_detail_chars", 300))
                if detail_chars < min_chars:
                    errors.append(
                        f"source section {source_id} has only {detail_chars} detail "
                        f"characters; requires {min_chars}"
                    )
                paragraphs = int(actual["paragraphs"])
                min_paragraphs = int(item.get("min_detail_paragraphs", 2))
                if paragraphs < min_paragraphs:
                    errors.append(
                        f"source section {source_id} has only {paragraphs} detail "
                        f"paragraphs; requires {min_paragraphs}"
                    )
            undeclared = sorted(set(parser.source_sections) - expected_ids)
            if undeclared:
                errors.append(
                    "HTML source sections missing from coverage file: "
                    + ", ".join(undeclared)
                )

        visuals = coverage.get("visuals", [])
        if not isinstance(visuals, list):
            errors.append("coverage visuals must be a list")
        else:
            for item in visuals:
                if not isinstance(item, dict) or not str(item.get("id", "")).strip():
                    errors.append("each coverage visual must have an id")
                    continue
                visual_id = str(item["id"]).lower()
                expected_mode = item.get("mode")
                expected_tag = {"image": "img", "html": "table"}.get(expected_mode)
                if expected_tag and parser.visual_tags.get(visual_id) != expected_tag:
                    errors.append(
                        f"{visual_id} expected {expected_mode} representation, found "
                        f"{parser.visual_tags.get(visual_id, 'none')}"
                    )
                if item.get("content_verified") is not True:
                    errors.append(f"{visual_id} is not marked content_verified")
                if expected_mode == "image" and item.get("crop_reviewed") is not True:
                    errors.append(f"{visual_id} image crop is not marked crop_reviewed")

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
    parser.add_argument("--coverage", type=Path)
    args = parser.parse_args()

    try:
        errors = validate(
            args.html, args.manifest, args.template, coverage_path=args.coverage
        )
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
