# Add RAG source freshness policy

<!-- daily-pr-task: rag-source-freshness-policy -->

RAG source freshness policy should flag stale, undated, or unknown-status sources before they are used in high-confidence answers. This makes legal and operational retrieval safer.

Policy checks:

- source status is known
- last reviewed date is present
- source age is within threshold
- stale sources require reviewer mode

## Portfolio Value

Shows retrieval quality accounts for stale or unknown legal/source metadata before answers are trusted.

## Validation

Run the unit test and confirm stale or undated sources are flagged.
