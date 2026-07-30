# Add LLM usage anomaly gate

<!-- daily-pr-task: llm-usage-anomaly-gate -->

Per-request token and cost ceilings do not detect a request that stays below hard limits but grows sharply relative to its accepted baseline. This offline gate validates observed prompt, completion, and cost metadata, enforces absolute budgets, and optionally detects total-token growth beyond a configured ratio. It supports release evaluation and incident triage without making paid provider calls.

## Portfolio Value

Adds deterministic observability guardrails for absolute token/cost overruns and relative usage growth without coupling CI to a live LLM provider.

## Validation

Run `python3 -m unittest discover -s tests` and confirm normal usage passes while absolute budget overruns, baseline growth anomalies, invalid observations, and invalid policy values fail.
