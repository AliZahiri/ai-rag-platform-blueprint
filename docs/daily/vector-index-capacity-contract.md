# Add vector index capacity contract

<!-- daily-pr-task: vector-index-capacity-contract -->

A RAG index requires capacity evidence before growth turns into silently degraded retrieval. This offline gate validates per-collection capacity observations: unique collection names, positive vector counts and capacity limits, utilization below a configurable threshold, and a declared shard count. It evaluates supplied metrics without querying a vector database.

## Portfolio Value

Makes vector-store capacity an explicit operational contract alongside existing RAG quality and restore controls.

## Validation

Run `python3 -m unittest discover -s tests` and confirm capacity headroom passes while empty input, duplicate collections, invalid counts or limits, exhausted utilization, invalid shard counts, and invalid policy values fail.
