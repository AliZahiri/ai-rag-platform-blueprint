# Add retrieval corpus lineage gate

<!-- daily-pr-task: retrieval-corpus-lineage-gate -->

Retrieval evaluation is not reproducible when evidence mixes corpus snapshots or vector-index builds. This offline gate validates unique source identities and requires every retrieved record to declare the expected corpus snapshot and index version. It consumes metadata only and never calls a model, provider, or vector store.

## Portfolio Value

Makes retrieval evidence reproducible by preventing silent mixing of corpus snapshots and vector-index versions in offline evaluation and release checks.

## Validation

Run `python3 -m unittest discover -s tests` and confirm consistent unique lineage passes while empty evidence, duplicate sources, snapshot/index mismatches, missing source identities, and invalid policy values fail.
