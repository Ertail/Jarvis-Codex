# Risk gates

Use a gate only when proceeding would consume authority or lock in an expensive
choice.

| Gate | Examples | Required response |
|---|---|---|
| Destructive | delete data, rewrite history, remove environments | Resolve exact target and obtain explicit authorization |
| External | deploy, publish, send, create or merge PR, change access | Confirm the destination and effect unless already explicitly authorized |
| Architectural | public API, schema, platform, security boundary | Present the smallest decision with consequences and recommendation |
| Ambiguous outcome | mutually exclusive product behavior or audience | Ask for the missing choice |
| New scope | work materially outside the requested outcome | Stop and propose a separate milestone |

No gate is needed for reversible local edits, normal verification, read-only
inspection, or reasonable implementation choices within the requested scope.
