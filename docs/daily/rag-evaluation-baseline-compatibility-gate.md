# Add RAG evaluation baseline compatibility gate

<!-- daily-pr-task: rag-evaluation-baseline-compatibility-gate -->

A candidate RAG evaluation should only be compared with a compatible baseline. This offline gate requires matching dataset digests, scorer versions, and metric sets plus a minimum sample count on both snapshots, preventing misleading regressions without provider calls.

## Portfolio Value

Makes RAG regression evidence statistically and semantically comparable before it is used as a release signal.

## Validation

Run python3 -m unittest discover -s tests and confirm only snapshots with the same dataset digest, scorer version, metric set, and adequate samples pass.
