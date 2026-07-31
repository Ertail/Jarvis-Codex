# Routing scenario catalog

`routing-cases.json` contains representative requests and expected routing
signals. It is an input catalog for manual or external model-based forward
evaluation.

`run_evals.py` validates:

- plugin manifest wiring;
- the exact skill and custom-agent inventory;
- required core-contract language and size budgets;
- scenario IDs, expectation fields, and referenced routes, skills, and agents.

It does **not** execute Codex or claim behavioral routing coverage. A future
runner may invoke fresh Codex sessions for each case, capture structured route
decisions, and compare them with these expectations.
