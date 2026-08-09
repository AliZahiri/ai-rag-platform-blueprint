# Add retrieval rerank result contract gate

<!-- daily-pr-task: retrieval-rerank-result-contract-gate -->

A reranker can silently return unknown, duplicate, weak, or incorrectly ordered chunks even when retrieval itself succeeds. This offline contract validates candidate identity, result rank continuity, score ordering, a minimum accepted score, and a bounded result count before reranked evidence enters the answer context. It consumes structured metadata only and makes no provider calls.

## Portfolio Value

Closes a retrieval quality gap between candidate generation and answer construction by rejecting malformed or low-confidence reranker output deterministically.

## Validation

Run `python3 -m unittest discover -s tests` and confirm valid descending rerank output passes while empty input, duplicate or unknown chunks, discontinuous ranks, non-finite or weak scores, ordering errors, excessive results, and invalid policies fail.
