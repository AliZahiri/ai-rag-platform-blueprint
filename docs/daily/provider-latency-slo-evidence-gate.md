# Add provider latency SLO evidence gate

<!-- daily-pr-task: provider-latency-slo-evidence-gate -->

Provider routing decisions should rely on a sufficiently sampled latency distribution and bounded error rate rather than a single request. This offline gate validates provider telemetry summaries, percentile ordering, a p95 budget, error-rate budget, sample coverage, and timezone-aware observation evidence without making paid provider calls.

## Portfolio Value

Adds provider-free operational evidence for latency and error budgets so fallback and routing policies can use stable distributions instead of anecdotal probes.

## Validation

Run python3 -m unittest discover -s tests and confirm invalid policies, insufficient samples, malformed or unordered percentiles, p95 breaches, error-rate breaches, and naive timestamps fail.
