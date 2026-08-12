# Add RAG evaluation dataset provenance gate

<!-- daily-pr-task: rag-evaluation-dataset-provenance-gate -->

RAG evaluation scores are only reproducible when the cases and source material are traceable. This offline gate validates evaluation-case metadata: unique case identifiers, an immutable source snapshot, non-empty expected answers and source identifiers, and a recent timezone-aware review timestamp. It checks supplied metadata only; it does not call a model or an external provider.

## Portfolio Value

Makes RAG evaluation results reviewable and reproducible by treating test cases and their source snapshots as release evidence, without adding paid provider calls to CI.

## Validation

Run `python3 -m unittest discover -s tests` and confirm reviewed traceable cases pass while empty, duplicate, incomplete, duplicate-source, stale, future, and invalid-policy records fail.
