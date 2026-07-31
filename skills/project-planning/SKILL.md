---
name: project-planning
description: Plan and coordinate risky, ambiguous, architectural, or multi-stage work without slowing ordinary changes. Use when a task has meaningful design choices, external or destructive effects, several dependent stages, long-running state, or an explicit request for a plan, roadmap, checkpoints, or phased delivery.
---

# Project Planning

Build the smallest plan that materially reduces execution risk.

## Route the task

Choose one route:

- **Direct**: one cohesive, reversible change with a known verification path.
- **Standard**: several dependent steps or files, but no unresolved high-cost
  decision. Maintain a live task plan and proceed.
- **Gated**: destructive or external effects, architecture with expensive
  downstream consequences, missing authority, or multiple materially different
  outcomes. Propose the decision and wait for Maverick.

Do not gate a task merely because it is new, spans three files, or has three
steps.

## Plan

1. State the outcome in one sentence.
2. Inspect current state before prescribing changes.
3. Separate decisions from mechanical work.
4. Map dependencies; parallelize only independent units.
5. Define verification for every milestone.
6. Note rollback or recovery for risky mutations.
7. Keep exactly one plan item in progress.

For work lasting across sessions or agent threads, create `.planning/STATE.md`
and record only durable state: decisions, current milestone, changed surfaces,
verification, blockers, and next action.

## Delegate selectively

Delegate only when explicitly requested or clearly required by this plan.
Prefer subagents for independent exploration, test execution, or bounded
implementation. Keep shared interfaces and shared files under one owner.

When delegating, provide:

- bounded objective and non-goals;
- authoritative inputs and relevant excerpts;
- allowed write scope;
- required verification;
- compact return contract from the root `AGENTS.md`.

## Execute and update

Proceed through reversible steps without repeated confirmation. Update the plan
when evidence invalidates an assumption. Pause only when the new route crosses
a gated boundary or materially changes the agreed outcome.

## Close

Verify milestone acceptance criteria, review the final diff, update durable
state, and report the outcome, evidence, limitations, and next recommended
milestone.

For risk examples and gate boundaries, read
[references/risk-gates.md](references/risk-gates.md).
