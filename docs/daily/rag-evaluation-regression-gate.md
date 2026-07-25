# Add RAG evaluation regression gate

<!-- daily-pr-task: rag-evaluation-regression-gate -->

A RAG release should compare quality metrics with an accepted baseline instead of evaluating only absolute thresholds. This deterministic gate checks groundedness, citation precision, and answer relevance on a normalized zero-to-one scale, rejects missing or non-finite scores, and blocks regressions larger than an explicit budget. It consumes offline evaluation results and never requires provider calls.

## Portfolio Value

Adds an offline, provider-independent release control that detects measurable RAG quality regressions across groundedness, citation precision, and relevance.

## Validation

Run `python3 -m unittest discover -s tests` and confirm bounded regressions pass while excessive, missing, non-finite, or out-of-range evaluation scores fail deterministically.
