# Add vector restore observation gate

<!-- daily-pr-task: vector-restore-observation-gate -->

A documented restore checklist does not prove that a restored vector collection is complete and queryable. This metadata-only gate validates expected record count and dimension, matching manifest digests, a successful sample similarity query, and a fresh timezone-aware verification timestamp. It does not contact a vector database in default CI.

## Portfolio Value

Moves vector recovery from checklist coverage to concrete restore evidence by verifying collection completeness, schema compatibility, integrity, queryability, and freshness.

## Validation

Run `python3 -m unittest discover -s tests` and confirm complete fresh restores pass while invalid counts, dimension or digest mismatches, failed sample queries, stale or naive timestamps, and invalid policy values fail.
