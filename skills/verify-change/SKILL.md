---
name: verify-change
description: Discover and run the repository's own validation commands after code, configuration, build, or documentation changes. Use when Codex must verify a change, determine available tests or linters, perform pre-commit checks, validate a generated artifact, or provide evidence before claiming completion.
---

# Verify Change

Use repository-native checks instead of imposing a global toolchain.

## Discover

Run:

```bash
python3 scripts/discover_checks.py [repo-root]
```

The script reports candidate commands from package manifests, task runners, CI
configuration, and common language layouts. It does not execute them.

Inspect the changed files and choose the smallest checks that cover their
behavior. Prefer explicit project documentation and CI commands over generic
defaults.

## Verify in layers

1. Syntax, parse, or compile check for changed files.
2. Narrow unit or targeted test.
3. Relevant lint and typecheck.
4. Primary execution-path smoke test.
5. Broader suite only when change risk warrants it.
6. Final diff and status check.

Do not run unrelated expensive suites by habit. Do not skip a required suite
because it is slow without reporting that limitation.

## Interpret

Distinguish:

- failure caused by the change;
- pre-existing failure;
- environment or dependency failure;
- unavailable check;
- check intentionally not run.

Fix in-scope failures, rerun the failed layer, and stop escalating after
repeated failures reveal a new blocker or scope boundary.

## Report

List exact commands and results. State unrun checks and why. Never claim
"verified" based only on the existence of a test file.

Read [references/command-selection.md](references/command-selection.md) when
several candidate commands exist or generated/monorepo layouts are involved.
