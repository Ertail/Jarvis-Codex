# Importing a Document Design System

Use this guide when Maverick supplies an HTML file, screenshot, image, or verbal
description for a new document style.

## Extract the system

Translate the reference into the shared token vocabulary:

- `--paper`, `--paper-2`: two background levels
- `--ink`, `--ink-soft`, `--ink-faint`: three text levels
- `--line`, `--line-strong`: two border levels
- `--ar*`, `--arb*`: semantic A/B colors, including deep, wash, and line values
- `--mono`, `--sans`: typography
- `--maxw`: readable canvas width

For HTML, inspect its CSS directly. For an image, estimate palette, contrast,
spacing, border, radius, and typographic character. For a verbal description,
turn adjectives into concrete tokens and component rules.

## Preserve the component contract

Start with:

```bash
python3 scripts/style_registry.py clone <new-name>
```

The clone is created under
`~/.codex/jarvis-codex/doc-style/design-systems/<new-name>/`. Edit its four
files:

- `design-system.css`
- `components.md`
- `template.html`
- `preview.html`

Retain the core class vocabulary so documents remain style-independent:
`.wrap`, `.hero`, `.toc`, `section.ch`, `.tldr`, `.call`, `.versus`,
`figure`, `.tbl-wrap`, `.stat-row`, `.chart-box`, `.stage-row`, `.gloss`,
and `.takeaways`.

Keep `figure img { max-width:100%; height:auto }`, responsive behavior, readable
contrast, print-safe spacing, and offline fallbacks. Do not add remote scripts or
images.

Replace the complete `<style>` block in both HTML files with the final
`design-system.css`; do not maintain divergent CSS copies.

## Validate and preview

Run:

```bash
python3 scripts/style_registry.py validate <new-name>
```

Render `preview.html` at desktop width and a narrow mobile width. Inspect
typography, hierarchy, tables, charts, overflow, and Korean glyphs. Show the
preview to Maverick and incorporate feedback.

Do not activate the new style until Maverick approves it. After approval:

```bash
python3 scripts/style_registry.py activate <new-name>
```

Keep previous systems registered so switching remains reversible.
