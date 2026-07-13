# Add citation source identifier policy

<!-- daily-pr-task: citation-source-id-policy -->

RAG citations should point to stable source identifiers so an answer can be audited after documents are re-indexed. The policy checks that every cited source has a unique non-empty identifier and a resolvable location.

## Portfolio Value

Demonstrates that RAG citations stay auditable through stable source references.

## Validation

Run `python3 -m unittest discover -s tests` and confirm duplicate source identifiers are rejected.
