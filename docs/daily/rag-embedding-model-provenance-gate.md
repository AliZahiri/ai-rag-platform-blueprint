# Add embedding model provenance gate

<!-- daily-pr-task: rag-embedding-model-provenance-gate -->

Changing an embedding model, revision, dimension, or index snapshot can silently invalidate retrieval comparisons. This offline release gate validates fresh provenance metadata against an explicitly approved embedding contract. It inspects only aggregate identifiers and hashes, makes no provider calls, and does not process document contents.

## Portfolio Value

Makes embedding-model changes auditable so retrieval quality or migration evidence cannot accidentally compare incompatible vector representations.

## Validation

Run python3 -m unittest discover -s tests and confirm only fresh evidence matching the approved model, revision, dimension, snapshot, and SHA-256 digest passes.
