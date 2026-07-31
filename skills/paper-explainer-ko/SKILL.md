---
name: paper-explainer-ko
description: Turn an academic-paper PDF into a faithful, self-contained Korean HTML explainer with chapter-level summaries, detailed walkthroughs, and every relevant figure and table. Always use when Maverick provides, attaches, or refers to a paper or research PDF and asks for a Korean explanation, summary, translation, study guide, document, or webpage, even when HTML or a skill is not explicitly mentioned. Explicit Korean triggers include "이 논문을 한국어로 쉽게 설명해줘", "이 논문 PDF를 그림과 표를 포함해서 한국어로 쉽게 설명해줘", "논문을 한글로 요약해줘", and equivalent wording.
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
- Give every substantive paper section a `.tldr` summary followed by a
  faithful, detailed Korean walkthrough.
- Preserve every numbered source section and subsection that contains material
  claims. Do not collapse several source subsections into one summary paragraph.
- Include every numbered figure and table. Rebuild a table as HTML only when
  its complete semantics can be preserved and verified; otherwise use a
  precisely reviewed crop.
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
5. Read `references/content-coverage.md` and create `work/coverage.json` from
   the complete source outline before composing.

Treat extraction as evidence, not layout truth. Resolve equations, multi-column
reading order, tables, and captions against rendered pages.

## Extract and embed visuals

Run the scripts from this skill directory with the bundled Python:

```bash
python3 scripts/extract_figures.py paper.pdf work/figures --tables
python3 scripts/embed_images.py work/figures work/datauris.json
```

The first command writes crops and `manifest.json`. View every final crop at
readable size. Reject crops that include neighboring prose, unrelated captions,
headers, or footers, even when the target visual itself is complete. Correct a
bad crop with an explicit PDF-point box:

```bash
python3 scripts/extract_figures.py paper.pdf work/figures \
  --only Figure4 --page 4 --box 300,556,562,664
```

Prefer searchable HTML only for tables that can be reproduced completely,
including multi-level headers, units, footnotes, grouping, and meaningful
emphasis. Verify reconstructed values cell-by-cell against the rendered page.
Use a crop whenever visual encoding or fidelity would be lost. Every embedded
image must use a `data:` URI. Add `data-figure="figureN"` to each figure image and
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
- detailed source blocks: preserve the paper hierarchy with one
  `data-source-section` container per entry in `work/coverage.json`;
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
  --coverage work/coverage.json \
  --template <resolved-style-directory>/template.html
```

Then open the HTML in the in-app browser, inspect the full page and a narrow
viewport, and verify:

- all figures and tables are present, legible, and correctly captioned;
- no image is remotely hotlinked;
- every chapter has a short summary followed by detailed coverage;
- every numbered source section and subsection in `coverage.json` is present,
  with important claims, methods, conditions, numbers, and conclusions
  translated or closely paraphrased;
- equations, numbers, citations, and limitations match the source;
- Korean reads naturally and technical terms are not over-translated;
- navigation, overflow, and responsive layout work.

Save the final artifact under `output/html/` unless Maverick chooses another
path. Return a clickable file link, the paper's one-line takeaway, and any
material extraction limitation.
