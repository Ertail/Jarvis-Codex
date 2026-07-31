#!/usr/bin/env python3
"""Crop numbered figures and optional tables from an academic PDF.

Uses pdfplumber, pypdfium2, and Pillow from the Codex workspace runtime. The
heuristic finds caption lines and clusters nearby PDF drawing/image objects
above each caption. Always inspect the resulting crops.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Iterable

import pdfplumber
from PIL import Image


CAPTION_RE = re.compile(
    r"^\s*(Figure|Fig\.?|Table)\s*(\d+)\s*[:.]",
    re.IGNORECASE,
)


def group_word_lines(words: list[dict], tolerance: float = 3.0) -> list[list[dict]]:
    lines: list[list[dict]] = []
    for word in sorted(words, key=lambda item: (item["top"], item["x0"])):
        if lines and abs(word["top"] - lines[-1][0]["top"]) <= tolerance:
            lines[-1].append(word)
        else:
            lines.append([word])
    for line in lines:
        line.sort(key=lambda item: item["x0"])
    return lines


def find_captions(page: pdfplumber.page.Page, want_tables: bool) -> list[dict]:
    captions: list[dict] = []
    words = page.extract_words(
        x_tolerance=2,
        y_tolerance=3,
        keep_blank_chars=False,
    )
    for line in group_word_lines(words):
        text = " ".join(word["text"] for word in line).strip()
        match = CAPTION_RE.match(text)
        if not match:
            continue
        kind = "Table" if match.group(1).lower().startswith("table") else "Figure"
        if kind == "Table" and not want_tables:
            continue
        captions.append(
            {
                "kind": kind,
                "num": int(match.group(2)),
                "label": f"{kind}{match.group(2)}",
                "bbox": [
                    min(word["x0"] for word in line),
                    min(word["top"] for word in line),
                    max(word["x1"] for word in line),
                    max(word["bottom"] for word in line),
                ],
                "text": text[:220],
            }
        )
    return captions


def object_rects(page: pdfplumber.page.Page, caption_top: float) -> list[tuple]:
    rects: list[tuple] = []
    objects: Iterable[dict] = (
        list(page.rects)
        + list(page.lines)
        + list(page.curves)
        + list(page.images)
    )
    for obj in objects:
        x0 = float(obj.get("x0", 0))
        x1 = float(obj.get("x1", 0))
        top = float(obj.get("top", 0))
        bottom = float(obj.get("bottom", top))
        width = abs(x1 - x0)
        height = abs(bottom - top)
        if bottom <= caption_top + 2 and max(width, height) > 3:
            rects.append((x0, top, x1, bottom))
    return rects


def cluster_near_caption(
    rects: list[tuple], caption_top: float, max_gap: float = 36
) -> list[tuple]:
    candidates = [rect for rect in rects if rect[3] <= caption_top + 2]
    if not candidates:
        return []
    candidates.sort(key=lambda rect: -rect[3])
    cluster = [candidates[0]]
    changed = True
    while changed:
        changed = False
        top = min(rect[1] for rect in cluster)
        bottom = max(rect[3] for rect in cluster)
        left = min(rect[0] for rect in cluster)
        right = max(rect[2] for rect in cluster)
        for rect in candidates:
            if rect in cluster:
                continue
            vertically_near = (
                rect[1] <= bottom + max_gap and rect[3] >= top - max_gap
            )
            horizontally_near = (
                rect[0] <= right + max_gap and rect[2] >= left - max_gap
            )
            if vertically_near and horizontally_near:
                cluster.append(rect)
                changed = True
    return cluster


def figure_bbox(
    page: pdfplumber.page.Page,
    caption: dict,
    all_captions: list[dict],
) -> tuple[float, float, float, float]:
    width = float(page.width)
    height = float(page.height)
    cap_x0, cap_top, cap_x1, _ = caption["bbox"]
    region_top = 0.085 * height
    for other in all_captions:
        other_bottom = other["bbox"][3]
        if other_bottom < cap_top - 4:
            region_top = max(region_top, other_bottom + 2)

    cluster = cluster_near_caption(
        [
            rect
            for rect in object_rects(page, cap_top)
            if rect[1] >= region_top - 2
        ],
        cap_top,
    )
    mid = width / 2
    spans_gutter = bool(
        cluster
        and min(rect[0] for rect in cluster) < mid - 30
        and max(rect[2] for rect in cluster) > mid + 30
    )
    if not spans_gutter and cap_x1 <= mid + 20:
        col_x0, col_x1 = 30.0, mid - 4
    elif not spans_gutter and cap_x0 >= mid - 20:
        col_x0, col_x1 = mid + 4, width - 30
    else:
        col_x0, col_x1 = 30.0, width - 30

    if cluster:
        x0 = min(rect[0] for rect in cluster)
        top = min(rect[1] for rect in cluster)
        x1 = max(rect[2] for rect in cluster)
        bottom = max(rect[3] for rect in cluster)
    else:
        x0, top, x1, bottom = cap_x0, region_top, cap_x1, cap_top - 2

    # Include nearby axis labels and titles without crossing the caption.
    for word in page.extract_words():
        center = (word["x0"] + word["x1"]) / 2
        if not col_x0 - 6 <= center <= col_x1 + 6:
            continue
        if not region_top - 2 <= word["top"] <= cap_top:
            continue
        overlaps = not (
            word["x1"] < x0 - 30
            or word["x0"] > x1 + 30
            or word["bottom"] < top - 34
            or word["top"] > bottom + 34
        )
        if overlaps:
            x0 = min(x0, word["x0"])
            x1 = max(x1, word["x1"])
            top = min(top, word["top"])
            bottom = max(bottom, word["bottom"])

    pad = 6
    return (
        max(26, col_x0, x0 - pad),
        max(54, region_top, top - pad),
        min(width - 26, col_x1, x1 + pad),
        min(cap_top - 1, bottom + pad),
    )


def render_crop(
    page: pdfplumber.page.Page,
    box: tuple[float, float, float, float],
    dpi: int,
) -> Image.Image:
    if box[2] <= box[0] or box[3] <= box[1]:
        raise ValueError(f"invalid crop box: {box}")
    return page.crop(box).to_image(resolution=dpi).original.convert("RGB")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=Path)
    parser.add_argument("outdir", type=Path)
    parser.add_argument("--dpi", type=int, default=300)
    parser.add_argument("--tables", action="store_true")
    parser.add_argument("--only")
    parser.add_argument("--box")
    parser.add_argument("--page", type=int)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)
    manifest: list[dict] = []

    with pdfplumber.open(args.pdf) as pdf:
        if args.only and args.box and args.page:
            page = pdf.pages[args.page - 1]
            box = tuple(float(value) for value in args.box.split(","))
            if len(box) != 4:
                raise ValueError("--box requires x0,top,x1,bottom")
            crop = render_crop(page, box, args.dpi)
            output = args.outdir / f"{args.only.lower()}.png"
            crop.save(output)
            print(f"[override] {args.only}: {crop.size} -> {output}")
            return 0

        for page_number, page in enumerate(pdf.pages, start=1):
            captions = find_captions(page, args.tables)
            for caption in captions:
                if (
                    args.only
                    and caption["label"].lower() != args.only.lower()
                ):
                    continue
                box = figure_bbox(page, caption, captions)
                crop = render_crop(page, box, args.dpi)
                filename = f"{caption['label'].lower()}.png"
                crop.save(args.outdir / filename)
                record = {
                    "label": caption["label"],
                    "kind": caption["kind"],
                    "page": page_number,
                    "file": filename,
                    "size_px": list(crop.size),
                    "box_pt": [round(value, 1) for value in box],
                    "caption": caption["text"],
                }
                manifest.append(record)
                print(
                    f"{caption['label']:10s} p{page_number} "
                    f"{crop.size} box={record['box_pt']}"
                )

    manifest_path = args.outdir / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\n{len(manifest)} crops -> {args.outdir}/ (manifest.json)")
    print("View every crop; use --only/--page/--box to fix loose or clipped crops.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
