# Add retrieval query distribution drift gate

<!-- daily-pr-task: retrieval-query-distribution-drift-gate -->

Retrieval quality can degrade when production query categories drift away from the evaluation baseline even if aggregate latency and success metrics remain healthy. This offline gate validates normalized baseline and candidate query-category distributions, minimum sample coverage, and a bounded total-variation distance without storing query text or user identifiers.

## Portfolio Value

Adds privacy-preserving distribution-shift evidence so evaluation coverage can be refreshed when real query categories change, rather than relying indefinitely on a stale aggregate benchmark.

## Validation

Run python3 -m unittest discover -s tests and confirm stable normalized distributions pass while undersampling, malformed probabilities, non-normalized distributions, excessive total-variation drift, and invalid policy fail.
