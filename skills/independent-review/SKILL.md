---
name: independent-review
description: Review code, plans, documents, designs, or completed work against requirements and external evidence. Use when the user requests a review, audit, critique, completeness check, risk assessment, second opinion, pre-merge verification, or independent validation of another agent's output.
---

# Independent Review

Find material defects, not stylistic preferences.

## Establish the contract

Identify the artifact, intended outcome, authoritative requirements, changed
scope, and available executable checks. If no external standard exists, say
which stakeholder lens or engineering principle is being used.

## Require independent evidence

A useful review must add at least one signal unavailable to the author:

- test, build, lint, typecheck, or reproduction output;
- original requirements, schema, or source-document comparison;
- authoritative documentation;
- a distinct stakeholder or threat-model lens for subjective work.

Do not treat rereading and opinion alone as verification.

## Review in this order

1. **Correctness**: wrong behavior, broken assumptions, invalid data flow.
2. **Safety and security**: destructive effects, trust boundaries, data leaks.
3. **Regression risk**: callers, consumers, compatibility, missing migration.
4. **Verification gaps**: important behavior without evidence.
5. **Completeness**: unmet or only partially met requirements.
6. **Maintainability**: only issues that create concrete future risk.

Ignore formatting or preference unless it hides a material problem.

## Report

Lead with findings ordered by severity. Each finding must include:

- severity;
- exact location or artifact section;
- concrete failure mode;
- supporting evidence;
- smallest safe remediation direction.

If there are no material findings, say so and list the checks performed and
remaining uncertainty. Do not invent issues to fill a report.

Use [references/review-rubric.md](references/review-rubric.md) for severity and
completeness criteria.
