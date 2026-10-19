# Add retrieval source owner coverage gate

<!-- daily-pr-task: retrieval-source-owner-coverage-gate -->

Source freshness alone does not establish who can approve a corpus change. This offline gate requires every retrieval source to carry a stable owner, a supported authority classification, and a recent ownership review. It validates metadata only and deliberately does not read source content.

## Portfolio Value

Adds explicit ownership evidence to corpus governance, so high-impact retrieval changes can be reviewed by an accountable source steward.

## Validation

Run python3 -m unittest discover -s tests and confirm owned, recent sources pass while duplicate, unowned, unsupported, stale, or future-dated metadata fails.
