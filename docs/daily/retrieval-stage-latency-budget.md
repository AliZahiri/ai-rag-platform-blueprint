# Add retrieval stage latency budget

<!-- daily-pr-task: retrieval-stage-latency-budget -->

End-to-end latency alone does not identify which retrieval stage exhausted the response budget. This offline policy requires explicit timing for every declared stage, rejects unknown or invalid observations, applies optional per-stage ceilings, and enforces a total retrieval budget. It consumes recorded metrics and never calls a model, vector store, or provider.

## Portfolio Value

Turns retrieval latency into actionable release evidence by enforcing both end-to-end and stage-specific budgets from deterministic recorded metrics.

## Validation

Run `python3 -m unittest discover -s tests` and confirm complete observations pass while missing or unknown stages, invalid values, per-stage overruns, total overruns, and malformed policy configuration fail.
