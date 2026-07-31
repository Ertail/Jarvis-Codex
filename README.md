# Jarvis Codex

Jarvis Codex is a thin operating layer for reliable work in Codex. It distills
the strongest parts of the original
[Jarvis Agent Universe](https://github.com/Ertail/Custom-Plugins) into Codex's
native instruction, skill, subagent, and worktree model.

It is intentionally smaller than the Claude Code harness. Codex remains the
executor; Jarvis adds durable working agreements and reusable workflows where
they materially improve safety or quality.

## What it adds

- A concise [`AGENTS.md`](AGENTS.md) contract for impact analysis, verification,
  state, delegation, and Git hygiene.
- Five goal-oriented skills:
  - `project-planning`
  - `grounded-research`
  - `independent-review`
  - `document-delivery`
  - `verify-change`
- Three project-scoped custom agents:
  - `jarvis_explorer` — read-only evidence gathering
  - `jarvis_reviewer` — independent, evidence-backed review
  - `jarvis_builder` — bounded implementation and verification
- Routing regression cases that guard against excessive ceremony and unsafe
  autonomy.

## Design principles

1. **Autonomy by default.** Reversible in-scope work proceeds without repeated
   confirmation.
2. **Gates for real risk.** Pause for destructive or external actions,
   high-cost architecture, missing authority, or materially ambiguous outcomes.
3. **Evidence over opinion.** Review adds tests, source requirements,
   authoritative documentation, reproductions, or a distinct stakeholder lens.
4. **Repository-native verification.** Discover the project's own commands
   instead of imposing one global toolchain.
5. **Selective delegation.** Use subagents for independent work when requested
   or directed by an applicable skill, not as default ceremony.
6. **Small durable context.** Keep always-on guidance concise and load detailed
   workflows only when their skill triggers.

## Use in this repository

Open the cloned repository as a Codex project. Codex discovers:

- `AGENTS.md` from the repository root;
- custom agents from `.codex/agents/`;
- project settings from `.codex/config.toml`.

The plugin manifest in `.codex-plugin/plugin.json` packages the skills for
plugin distribution. During source development, the repository remains the
authoritative copy.

## Invoke a workflow

Skills can trigger from user intent or be invoked explicitly:

```text
Use $project-planning to plan this multi-stage migration.
Use $grounded-research to compare these technologies.
Use $independent-review to review this branch against the requirements.
Use $document-delivery to turn these sources into an executive brief.
Use $verify-change to discover and run the right checks.
```

Subagents should be requested explicitly when useful:

```text
Delegate repository mapping to jarvis_explorer and test-risk review to
jarvis_reviewer, then combine their evidence before changing code.
```

## Development and validation

Run all local checks:

```bash
python3 evals/run_evals.py
python3 -m unittest discover -s skills/verify-change/tests -v
```

Validate every skill with Codex's `skill-creator` validator and validate the
plugin with `plugin-creator` before release. The exact validator paths depend on
the local Codex installation and are intentionally not embedded in the
repository.

## Project status

Version `0.1.0` is the first Codex-native baseline:

- Core working agreement: complete
- Workflow skills: complete
- Minimal custom agents: complete
- Plugin package and routing evals: complete

The original migration analysis remains available in
[`codex-harness-analysis.html`](codex-harness-analysis.html).
