---
name: doc-style
description: Apply and manage Maverick's swappable house style for readable HTML documents. Use whenever Codex creates a report, brief, research synthesis, diagnosis, comparison, study guide, technical explainer, or other multi-section document as HTML; default to the active paper-ink style unless Maverick requests another registered style. Also use when listing, previewing, importing, registering, validating, or switching document styles.
---

# Document Style Registry

Create readable HTML documents from the active, swappable design system. Keep
content generation separate from presentation so a later style switch does not
change document semantics.

## Resolve the active style

Run:

```bash
python3 scripts/style_registry.py active
python3 scripts/style_registry.py resolve
python3 scripts/style_registry.py validate
```

The packaged default and persistent user registry are:

```text
<skill>/active.txt                         # packaged default
<skill>/assets/design-systems/<name>/      # built-in styles
~/.codex/jarvis-codex/doc-style/
  active.txt                               # persistent user choice
  design-systems/<name>/                   # imported user styles
```

Use the path printed by `resolve`; do not assume the style is packaged. Read
that system's `components.md`. For a first use or visual review, also inspect
`preview.html`.

## Apply a style

1. Copy `<resolved-path>/template.html` to the requested output path.
2. Preserve the template's `<style>` block byte-for-byte.
3. Replace placeholder content using documented components.
4. Include at least one decision-relevant visualization when the content
   supports one: a comparison table, metric tiles, flow, timeline, chart, or
   explanatory diagram. Never invent quantitative data to manufacture a chart.
5. Use inline SVG or CSS for custom visualizations. Use the system tokens and
   place the visual in `.chart-box`, `figure`, or another documented container.
6. Keep the output self-contained: inline SVG/CSS, data-URI images, and no
   external script or image dependencies. The font imports may remain because
   the style provides offline fallbacks.
7. Render the completed HTML in a browser, inspect desktop and narrow layouts,
   and fix clipping, overlap, illegible labels, and broken navigation.

Do not use this skill for application UI, dashboards, slide decks, source code,
or a native editable format explicitly requested by Maverick.

## Switch a registered style

List styles and activate one:

```bash
python3 scripts/style_registry.py list
python3 scripts/style_registry.py activate <name>
```

Only activate a style when Maverick explicitly requests the switch. The choice
is stored under `~/.codex/jarvis-codex/`, survives plugin reinstalls, and affects
new documents only.

## Import a new style

Read [references/import-guide.md](references/import-guide.md), then:

1. Clone the active component contract with
   `python3 scripts/style_registry.py clone <new-name>`.
2. Adapt tokens and component presentation without renaming core classes.
3. Regenerate `template.html` and `preview.html` so their inline CSS exactly
   matches `design-system.css`.
4. Run `python3 scripts/style_registry.py validate <new-name>`.
5. Render and show the preview to Maverick.
6. Activate only after Maverick approves the preview.

Never delete an existing registered system as part of a style import.
