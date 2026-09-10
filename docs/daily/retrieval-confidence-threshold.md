# Add retrieval confidence threshold policy

<!-- daily-pr-task: retrieval-confidence-threshold -->

Retrieved sources should meet a configurable confidence threshold before they are used to ground an answer. The policy makes low-confidence retrieval visible instead of silently turning weak context into a confident response.

Scores must be finite numeric probabilities. Boolean values, `NaN`, infinity, and values outside the inclusive `0..1` range fail closed as low-confidence evidence; the configured minimum must satisfy the same numeric contract.

## Portfolio Value

Makes RAG answer quality controls explicit through a deterministic retrieval confidence gate.

## Validation

Run `python3 -m unittest discover -s tests` and confirm low-confidence sources are reported.
