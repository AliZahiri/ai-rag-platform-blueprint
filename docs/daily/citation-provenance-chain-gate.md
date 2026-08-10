# Add citation provenance-chain gate

<!-- daily-pr-task: citation-provenance-chain-gate -->

Citation freshness alone is insufficient when source material crosses ingestion and indexing stages. This offline gate validates a citation provenance chain: each citation has a unique source identifier, immutable content digest, source capture timestamp, and index snapshot matching the answer's declared snapshot. It rejects incomplete, duplicate, stale, or cross-snapshot evidence without reading source documents.

## Portfolio Value

Makes RAG answers auditable across source capture and vector-index snapshots instead of relying on a bare citation label.

## Validation

Run `python3 -m unittest discover -s tests` and confirm complete immutable provenance passes while empty input, duplicate source identifiers, invalid digests, naive timestamps, cross-snapshot citations, and invalid snapshot contracts fail.
