# Add RAG provider cost anomaly evidence gate

<!-- daily-pr-task: rag-cost-anomaly-evidence-gate -->

This offline gate requires a provider name, finite observed and baseline costs, and a timezone-aware timestamp. It rejects evidence above the daily spend cap, above the configured growth ratio, or recorded in the future.

## Portfolio Value

Adds a reviewable cost-control contract for provider fallback and token-budget operations.

## Validation

Run python3 -m unittest discover -s tests. Tests cover compliant evidence, missing provider data, spend-cap and growth anomalies, future timestamps, and invalid policy or clock values.
