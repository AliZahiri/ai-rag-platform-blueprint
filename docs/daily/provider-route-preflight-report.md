# Add provider route preflight report

<!-- daily-pr-task: provider-route-preflight-report -->

Provider selection should expose one structured preflight report covering required capabilities, context-window fit, and configured token budget before any paid request. The report keeps routing failures machine-readable and operates only on declared metadata.

## Portfolio Value

Turns provider metadata policies into an auditable route selection report before latency or paid usage is incurred.

## Validation

Run `python3 -m unittest discover -s tests` and confirm capability, context, and token-budget violations are aggregated deterministically.
