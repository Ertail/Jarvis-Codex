# Content Coverage Contract

The explainer is a faithful Korean walkthrough, not an executive summary.
Preserve the paper's numbered hierarchy and cover material content before
adding interpretation.

## Build the coverage plan

Create `work/coverage.json` after reading the complete paper and before writing
the HTML:

```json
{
  "sections": [
    {
      "id": "3.1",
      "title": "Pre-training Data",
      "min_detail_chars": 500,
      "min_detail_paragraphs": 3
    }
  ],
  "visuals": [
    {
      "id": "table2",
      "mode": "image",
      "crop_reviewed": true,
      "content_verified": true
    }
  ]
}
```

Include every numbered main section and subsection that contains substantive
claims, methods, experiments, results, limitations, or conclusions. A short
administrative appendix may use one paragraph and a lower character threshold;
do not lower thresholds merely to make validation pass.

Wrap the detailed Korean treatment of each entry in exactly one container:

```html
<div class="source-section" data-source-section="3.1">
  <h3 class="sub">3.1 사전학습 데이터</h3>
  <p>...</p>
  <p>...</p>
</div>
```

The chapter `.tldr` remains outside these containers. Tables do not count as
detail prose.

## What “covered” means

For each source section or subsection:

1. Translate or closely paraphrase every material claim and method step.
2. Preserve named datasets, model components, hyperparameters, experimental
   conditions, important numbers, comparisons, and author-stated limitations.
3. Explain the rationale and causal chain, not only the result.
4. Explain equations, algorithms, and ablations in prose; retain notation when
   it carries meaning.
5. Separate the authors' claims from the explainer's interpretation.
6. Compress only repetition, generic transitions, citations that add no
   substantive content, and boilerplate.

Use the source length and density to set honest minimums in `coverage.json`.
As a normal floor, use at least two substantive paragraphs and 300 Korean
detail characters per source section. Dense method or evaluation subsections
usually need three or more paragraphs and 500 or more characters.

## Tables and figures

- Reconstruct a table as HTML only when every header, row, column, unit,
  footnote, grouping, and meaningful emphasis can be preserved and checked
  cell-by-cell against the rendered source.
- Use an image for multi-level headers, layout-dependent grouping, dense
  benchmark emphasis, or any table whose meaning would be weakened by
  reconstruction.
- An image crop must include the complete visual and its intrinsic labels, with
  no neighboring body paragraph, unrelated caption, header, or footer.
- Inspect every final crop at readable size. If it is loose, clipped, or
  blurry, rerun extraction with an explicit box.
- Set `content_verified` only after comparing the final representation against
  the rendered PDF. Set `crop_reviewed` only after visually inspecting the
  exact embedded crop.
