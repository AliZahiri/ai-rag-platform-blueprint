# Add response safety classification gate

<!-- daily-pr-task: response-safety-classification-gate -->

A response should carry an explicit safety decision before release, rather than relying on a gateway status code alone. This offline gate validates safety evidence: a unique response identifier, a supported classification, a bounded confidence score, and a release decision consistent with the classification. It does not call a moderation provider.

## Portfolio Value

Complements prompt and PII controls with a deterministic release boundary for response-level safety decisions.

## Validation

Run `python3 -m unittest discover -s tests` and confirm confident safe responses pass while empty input, duplicate IDs, invalid classifications, unbounded confidence, low-confidence safe decisions, release mismatch, and invalid policy values fail.
