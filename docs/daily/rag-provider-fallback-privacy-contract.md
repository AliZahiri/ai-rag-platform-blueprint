# Add provider fallback privacy contract gate

<!-- daily-pr-task: rag-provider-fallback-privacy-contract -->

A primary provider can satisfy privacy policy while an emergency fallback silently weakens residency, retention, or training-use guarantees. This offline gate evaluates every provider in each declared route, requires a real fallback, and rejects privacy downgrades before routing configuration is promoted. It inspects policy metadata only and never sends prompts or credentials to providers.

## Portfolio Value

Prevents an availability fallback from becoming an unreviewed privacy downgrade and demonstrates policy composition across routing and data-governance controls.

## Validation

Run python3 -m unittest discover -s tests and confirm every primary/fallback provider must use an approved region, bounded retention, disabled training use, and unique identifiers.
