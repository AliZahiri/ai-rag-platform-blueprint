# Add index replica consistency evidence gate

<!-- daily-pr-task: rag-index-replica-consistency-evidence-gate -->

A healthy replica can still serve stale or structurally different retrieval data. This offline release gate verifies that independent vector index replicas report the approved generation, document count, content digest, health state, and a recent observation timestamp. Evidence contains only aggregate metadata and hashes, never source content.

## Portfolio Value

Makes multi-replica retrieval readiness depend on fresh content-equivalence evidence instead of health status alone.

## CI usage

The evidence file must contain a top-level `replicas` array. Each replica reports
its unique ID, health state, index generation, document count, SHA-256 content
digest, and timezone-aware `observed_at` timestamp. Keep the approved generation,
count, and digest in trusted CI variables instead of accepting them from the
evidence producer.

```bash
python3 scripts/index_replica_consistency.py replica-evidence.json \
  --expected-generation "$APPROVED_INDEX_GENERATION" \
  --expected-document-count "$APPROVED_DOCUMENT_COUNT" \
  --expected-sha256 "$APPROVED_INDEX_SHA256" \
  --maximum-age-seconds 900
```

The command emits one JSON report to standard output. Exit code `0` means the
evidence passes, `1` means the replica policy failed, and `2` means the evidence
or command policy is invalid. Use `--now` in deterministic CI fixtures.

## Validation

Run `python3 -m unittest discover -s tests` and confirm at least two healthy
replicas must match the approved generation, count, digest, and freshness window.
