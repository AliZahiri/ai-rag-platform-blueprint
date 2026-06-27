# Add document chunking profile policy

<!-- daily-pr-task: chunking-profile-policy -->

Document chunking should be explicit and testable. Chunk size, overlap, and parser name affect retrieval quality and should be tracked with the embedding model.

Policy checks:

- chunk size is bounded
- overlap is smaller than chunk size
- parser profile is named
- embedding model is recorded

## Portfolio Value

Demonstrates RAG ingestion controls for repeatable retrieval quality.

## Validation

Run the unit test and confirm overlap is smaller than chunk size.
