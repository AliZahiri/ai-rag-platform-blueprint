# Add embedding migration readiness gate

<!-- daily-pr-task: embedding-migration-readiness-gate -->

Changing embedding models can make an existing vector index unreadable or degrade retrieval during backfill. This offline release gate requires explicit source and target dimensions, completed dual-write backfill, successful sample queries against both indexes, and a minimum top-result overlap before traffic moves to the target embedding. It evaluates supplied migration evidence without calling a model or vector store.

## Portfolio Value

Adds an explicit, measurable release boundary for embedding upgrades so dimension changes and incomplete backfills cannot silently break production retrieval.

## Validation

Run `python3 -m unittest discover -s tests` and confirm complete dual-index evidence passes while invalid dimensions, undersized samples, invalid or weak overlap, incomplete backfill, failed queries, and invalid policies fail.
