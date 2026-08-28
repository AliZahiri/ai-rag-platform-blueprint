# Add LLM usage reconciliation gate

<!-- daily-pr-task: llm-usage-reconciliation-gate -->

Gateway token metrics should reconcile with provider usage summaries before cost and capacity reports are trusted. This offline gate validates unique request records, non-negative token and cost measurements, and configurable deltas for request count, input tokens, output tokens, and cost. It consumes exported aggregates and makes no paid provider calls.

## Portfolio Value

Turns token and cost observability into auditable accounting evidence by detecting missing, duplicated, or drifted usage before reports drive budgets.

## Validation

Run python3 -m unittest discover -s tests and confirm duplicate requests, invalid measurements, count/token drift, cost drift, and invalid tolerances fail.
