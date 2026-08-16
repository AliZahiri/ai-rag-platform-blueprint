# Add RAG ingestion source manifest contract

<!-- daily-pr-task: rag-ingestion-source-manifest-contract -->

RAG ingestion should preserve a reviewable source manifest before embeddings are published. This offline contract validates a stable source identifier, a content digest, a timezone-aware retrieval timestamp, and a declared license so downstream retrieval and citation controls can reason about provenance without provider calls.

## Portfolio Value

Extends RAG ingestion controls with deterministic provenance evidence that supports traceable retrieval, citations, and license review.

## Validation

Run `python3 -m unittest discover -s tests` and confirm only manifests with a source ID, SHA-256 digest, timezone-aware retrieval time, and license pass.
