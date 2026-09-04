# Add index replica consistency evidence gate

<!-- daily-pr-task: rag-index-replica-consistency-evidence-gate -->

A healthy replica can still serve stale or structurally different retrieval data. This offline release gate verifies that independent vector index replicas report the approved generation, document count, content digest, health state, and a recent observation timestamp. Evidence contains only aggregate metadata and hashes, never source content.

## Portfolio Value

Makes multi-replica retrieval readiness depend on fresh content-equivalence evidence instead of health status alone.

## Validation

Run python3 -m unittest discover -s tests and confirm at least two healthy replicas must match the approved generation, count, digest, and freshness window.
