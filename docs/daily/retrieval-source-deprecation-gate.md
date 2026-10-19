# Add retrieval source deprecation gate

<!-- daily-pr-task: retrieval-source-deprecation-gate -->

A retired source must not silently remain available to retrieval after its support window ends. This offline gate validates non-content deprecation metadata: unique source identifiers, a timezone-aware effective date, a documented replacement or removal disposition, and no future-dated retirement evidence. It does not delete documents or query a vector database.

## Portfolio Value

Preserves answer quality and source traceability by making corpus retirement and replacement decisions explicit before an obsolete document remains retrievable.

## Validation

Run python3 -m unittest discover -s tests and confirm dated, unique removal or replacement records pass while future, duplicate, or undocumented replacements fail.
