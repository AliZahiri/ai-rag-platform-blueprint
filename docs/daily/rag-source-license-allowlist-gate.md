# Add RAG source license allowlist gate

<!-- daily-pr-task: rag-source-license-allowlist-gate -->

RAG ingestion should reject sources whose license is missing, unapproved, or incompatible with the collection policy. This offline gate normalizes license identifiers, prevents duplicate source records, and keeps policy decisions reviewable without making provider calls.

## Portfolio Value

Adds a deterministic licensing control to RAG ingestion so provenance checks can block unreviewed content before it reaches retrieval.

## Validation

Run `python3 -m unittest discover -s tests` and confirm unique allowlisted sources pass while missing, duplicate, and unapproved licenses fail.
