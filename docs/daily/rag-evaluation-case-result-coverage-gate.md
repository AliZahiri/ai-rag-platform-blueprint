# Add RAG evaluation case result coverage gate

<!-- daily-pr-task: rag-evaluation-case-result-coverage-gate -->

A release evaluation must account for every declared case exactly once. This offline gate validates unique expected case identifiers, unique result records, explicit pass/fail status, and rejects missing or unexpected cases without invoking a model provider.

## Portfolio Value

Makes evaluation completeness a deterministic release signal so aggregate scores cannot silently omit difficult or failed cases.

## Validation

Run python3 -m unittest discover -s tests and confirm missing, duplicate, malformed, or unexpected evaluation results fail.
