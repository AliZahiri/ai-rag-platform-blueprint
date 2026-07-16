# Add retrieval source deduplication helper

<!-- daily-pr-task: retrieval-source-deduplication -->

RAG retrieval can return overlapping chunks from the same source. Deduplicating stable source identifiers before answer generation keeps context focused, reduces token cost, and makes citation counts meaningful.

## Portfolio Value

Adds a small but production-relevant retrieval control for context efficiency and trustworthy citations.

## Validation

Run `python3 -m unittest discover -s tests` and confirm duplicate source identifiers are detected deterministically.
