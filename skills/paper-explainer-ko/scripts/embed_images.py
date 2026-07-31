#!/usr/bin/env python3
"""
embed_images.py - Downscale PNGs and emit base64 data URIs for offline embedding.

The final HTML must be fully self-contained (no remote <img> src), so every
figure is inlined as a data URI. This script downscales each image to a sane
max width (keeps file size reasonable while staying crisp) and writes a JSON
map {label: "data:image/png;base64,...."} you can splice into the HTML.

Usage:
  python embed_images.py figs figs/datauris.json
  python embed_images.py figs figs/datauris.json --full-width fig1,fig3,fig8

By default column figures are capped at 1200px wide and full-width figures at
1600px (tuned for the doc-style 1080px canvas, where figures display at up to
~990px). Pass --full-width with a comma list of stems to widen specific ones.
"""
import os, sys, io, json, base64, argparse
from PIL import Image


def data_uri(path, maxw):
    im = Image.open(path).convert("RGB")
    if im.width > maxw:
        im = im.resize((maxw, round(im.height * maxw / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, format="PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode(), len(buf.getvalue())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("indir")
    ap.add_argument("outjson")
    ap.add_argument("--full-width", default="", help="comma list of stems to render at the --wide cap")
    ap.add_argument("--wide", type=int, default=1600)
    ap.add_argument("--narrow", type=int, default=1200)
    args = ap.parse_args()

    wide = {s.strip().lower() for s in args.full_width.split(",") if s.strip()}
    out = {}
    total = 0
    for fn in sorted(os.listdir(args.indir)):
        if not fn.lower().endswith((".png", ".jpg", ".jpeg")):
            continue
        stem = os.path.splitext(fn)[0].lower()
        maxw = args.wide if stem in wide else args.narrow
        uri, sz = data_uri(os.path.join(args.indir, fn), maxw)
        out[stem] = uri
        total += len(uri)
        print(f"{stem:12s} {round(sz/1024):5d} KB png  ->  {round(len(uri)/1024):5d} KB b64")

    with open(args.outjson, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False)
    print(f"\n{len(out)} images -> {args.outjson}  (~{round(total/1024/1024,2)} MB base64 total)")


if __name__ == "__main__":
    main()
