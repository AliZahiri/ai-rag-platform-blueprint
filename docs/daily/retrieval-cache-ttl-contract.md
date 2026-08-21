# Add retrieval cache expiration contract

<!-- daily-pr-task: retrieval-cache-ttl-contract -->

Retrieval cache entries must have an explicit bounded lifetime and remain safe to serve. This offline contract rejects missing citation scopes, invalid timestamps, excessive TTLs, and entries marked as sensitive so cached retrieval cannot silently outlive its review assumptions.

## Portfolio Value

Makes retrieval-cache safety explicit through bounded lifetimes and evidence that sensitive entries are not served from cache.

## Validation

Run `python3 -m unittest discover -s tests` and confirm valid cache entries require a bounded TTL, timezone-aware timestamp, and non-sensitive classification.
