---
name: paper-explainer-ko
description: Turn an academic-paper PDF into a faithful, self-contained Korean HTML explainer with chapter-level summaries, detailed walkthroughs, and every relevant figure and table. Use when Maverick provides or points to a research-paper or arXiv PDF and asks for a Korean explanation, summary, translation, study guide, document, or webpage, even when HTML or a skill is not explicitly mentioned.
---

# Korean Paper Explainer

Produce one self-contained Korean HTML file that lets a technical reader
understand the paper without constantly returning to the source.

## Preserve the contract

- Write headings, prose, captions, glossary, and takeaways in natural Korean.
- Keep established model, dataset, method, metric, and practitioner terms in
  English when Korean would be awkward. On first use, prefer `한글(English)`
  where that pairing helps.
- Keep the original English title next to its Korean rendering.
- Give every substantive paper section a `.tldr` summary followed by detail.
- Include every numbered figure and table. Rebuild ordinary tables as HTML;
  crop visually complex tables.
- Use only claims and numbers supported by the paper. Label any reconstruction
  clearly.
- Use the active sibling `$doc-style` design system. Do not carry a private CSS
  copy in this skill.

## Prepare the source

Read the bundled `$pdf` skill completely before processing the paper. Use its
workspace runtime and Poppler paths rather than installing into the system
Python.

1. Inspect metadata and page count with `pdfinfo`.
2. Render every page to PNG and visually inspect the paper structure.
3. Extract text with `pdftotext -layout`; use `pdfplumber` or `pypdf` as a
   fallback. Read the complete paper, including appendices and captions.
4. Record the title, authors, affiliation, venue/year, source URL, section
   order, claims, limitations, figures, and tables.

Treat extraction as evidence, not layout truth. Resolve equations, multi-column
reading order, tables, and captions against rendered pages.

## Extract and embed visuals

Run the scripts from this skill directory with the bundled Python:

```bash
python3 scripts/extract_figures.py paper.pdf work/figures --tables
python3 scripts/embed_images.py work/figures work/datauris.json
```

The first command writes crops and `manifest.json`. View every crop. Correct a
bad crop with an explicit PDF-point box:

```bash
python3 scripts/extract_figures.py paper.pdf work/figures \
  --only Figure4 --page 4 --box 300,556,562,664
```

Prefer searchable HTML for ordinary tables. Use a crop for a table whose visual
encoding would be lost during reconstruction. Every embedded image must use a
`data:` URI. Add `data-figure="figureN"` to each figure image and
`data-figure="tableN"` to either the reconstructed `<table>` or table image so
the validator can match it to the manifest.

If the paper has no useful native visual, create an evidence-grounded inline
SVG concept map, method flow, or comparison. Do not create a numeric chart from
unstated values.

## Compose with the active document style

Resolve the persistent active style:

```bash
python3 ../doc-style/scripts/style_registry.py active
python3 ../doc-style/scripts/style_registry.py resolve
```

Read `components.md` and `template.html` from the resolved directory. Copy the
template and preserve its `<style>` block byte-for-byte. Fill:

- hero: Korean title, English original, authors, affiliation, venue/year,
  source, and the paper's thesis;
- table of contents: paper sections plus limitations, glossary, and takeaways;
- chapters: one per substantive section, each starting with `.tldr`;
- figures and tables: placed where the paper introduces or analyzes them;
- synthesis: contributions, evidence, limitations, practical implications,
  glossary, and four to six takeaways.

Map the two semantic colors consistently when the argument has a meaningful
contrast. Do not force a false dichotomy.

## Validate and render

Run:

```bash
python3 scripts/validate_explainer.py output.html \
  --manifest work/figures/manifest.json \
  --template <resolved-style-directory>/template.html
```

Then open the HTML in the in-app browser, inspect the full page and a narrow
viewport, and verify:

- all figures and tables are present, legible, and correctly captioned;
- no image is remotely hotlinked;
- every chapter has a summary and detail;
- equations, numbers, citations, and limitations match the source;
- Korean reads naturally and technical terms are not over-translated;
- navigation, overflow, and responsive layout work.

Save the final artifact under `output/html/` unless Maverick chooses another
path. Return a clickable file link, the paper's one-line takeaway, and any
material extraction limitation.
