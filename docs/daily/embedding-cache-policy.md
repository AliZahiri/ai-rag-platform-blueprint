# Add embedding cache policy

<!-- daily-pr-task: embedding-cache-policy -->

Embedding cache policy should avoid recomputing vectors when document content and ingestion settings are unchanged. Cache keys must include the embedding model and parser profile to prevent stale reuse.

Cache key inputs:

- document id
- content checksum
- parser profile
- embedding model

## Portfolio Value

Shows RAG ingestion cost and latency are controlled by deterministic cache keys.

## Validation

Run the unit test and confirm cache keys include document id, parser profile, and embedding model.
