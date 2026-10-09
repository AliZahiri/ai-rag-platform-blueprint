# Add RAG evaluation metric contract gate

<!-- daily-pr-task: rag-evaluation-metric-contract-gate -->

Evaluation comparisons need stable metric identities, directions, finite values,
and an explicit regression budget before a release decision can be trusted. This
offline gate supports both normalized quality scores and unbounded operational
measurements such as latency or cost; it does not process RAG content or call a
provider.

Each metric requires a lower-case `snake_case` `metric_id`, a direction of
`higher_is_better` or `lower_is_better`, `baseline` and `candidate` values, and
a non-negative `maximum_regression`. A candidate fails when its directional
regression exceeds that budget.

## Portfolio Value

Adds a deterministic release control so malformed or directionally ambiguous
evaluation evidence cannot silently approve a RAG regression.

## Validation

Run `python3 -m unittest discover -s tests`. The focused tests cover valid
higher- and lower-is-better comparisons, rejected regressions, non-finite
numbers, invalid identifiers, and malformed inputs.
