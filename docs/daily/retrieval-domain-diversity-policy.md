# Add retrieval domain diversity policy

<!-- daily-pr-task: retrieval-domain-diversity-policy -->

High-scoring chunks can still represent one publisher or document family. This deterministic policy measures distinct normalized source domains, ignores malformed sources, and requires an explicit minimum before a multi-source answer is treated as diverse. It complements score, deduplication, and citation checks without provider calls.

## Portfolio Value

Adds a measurable retrieval-quality control that limits single-source concentration before grounded answers are promoted.

## Validation

Run `python3 -m unittest discover -s tests` and confirm domain normalization, duplicate collapse, and invalid policy bounds are covered.
