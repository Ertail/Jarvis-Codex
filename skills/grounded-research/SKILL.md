---
name: grounded-research
description: Investigate codebases, documents, technologies, products, or external questions with traceable evidence and calibrated confidence. Use when the user asks to research, compare, audit, investigate, scan a repository, verify a current claim, synthesize multiple sources, or distinguish facts from assumptions.
---

# Grounded Research

Answer the real decision with the minimum sufficient evidence.

## Frame

1. Restate the decision or question.
2. Split it into independent evidence tracks.
3. Identify which claims are local, current, niche, or high stakes.
4. Choose authoritative sources before broad discovery.

Use repository files and executable behavior for local claims. Use official
documentation or primary sources for technical claims. Use connectors for
private workspace data. Browse when information may have changed or the user
requests current information.

## Scan, then deepen

Start broad enough to map the landscape. Deepen only where:

- sources disagree;
- a claim controls the recommendation;
- the subject is version-sensitive;
- confidence is low;
- the cost of error is high.

Independent evidence tracks may run in parallel when explicitly requested or
when an applicable instruction authorizes subagents.

## Record evidence

For every material conclusion, retain:

- claim;
- source or executable observation;
- date/version when relevant;
- confidence;
- contradiction or limitation.

Separate observation from inference. Never present an inference as a quoted or
directly observed fact.

## Synthesize

Lead with the answer. Explain the strongest supporting evidence, important
conflicts, and what would change the conclusion. Cite web sources near the
claim and use file paths or symbols for repository evidence.

Do not dump raw search results or long notes. Store large intermediate evidence
in a file and return a compact synthesis.

Read [references/evidence-ladder.md](references/evidence-ladder.md) when source
quality, conflicts, or confidence calibration are material.
