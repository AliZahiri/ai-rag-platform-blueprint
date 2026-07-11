# Add RAG evaluation snapshot helper

<!-- daily-pr-task: rag-evaluation-snapshot -->

RAG quality should be checked with repeatable snapshots, not only ad hoc chat testing. A compact evaluation snapshot can track whether answers include citations, whether retrieval returned enough sources, and whether freshness requirements were met.

Suggested snapshot fields:

- question id
- retrieved source count
- answer includes citation
- source freshness status
- reviewer outcome

## Portfolio Value

Connects RAG platform work to measurable evaluation and answer quality controls.

## Validation

Run `python3 -m unittest discover -s tests` and confirm incomplete snapshots produce actionable warnings.
