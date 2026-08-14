# Add retrieval indexing freshness gate

<!-- daily-pr-task: retrieval-indexing-freshness-gate -->

A retrieval result is only as current as the indexed source behind it. This offline gate validates unique source identities, immutable content digests, timezone-aware source and indexing timestamps, and a bounded indexing delay. It evaluates supplied metadata only and never connects to a vector database.

## Portfolio Value

Makes source freshness a concrete indexing-service-level release signal, complementing retrieval quality and citation checks without requiring a live provider.

## Validation

Run `python3 -m unittest discover -s tests` and confirm recent indexed sources pass while empty, duplicate, invalid-digest, stale, delayed, future, malformed, and invalid-policy records fail.
