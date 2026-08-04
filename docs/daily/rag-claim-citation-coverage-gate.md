# Add RAG claim citation coverage gate

<!-- daily-pr-task: rag-claim-citation-coverage-gate -->

Answer-level citation presence can hide unsupported substantive claims. This deterministic gate validates unique claim identities, known citation references, and a configurable minimum ratio of support-required claims with citations. It evaluates structured answer metadata without calling an LLM or provider.

## Portfolio Value

Makes citation traceability claim-aware by measuring whether substantive answer claims are actually connected to known evidence instead of merely counting citations.

## Validation

Run `python3 -m unittest discover -s tests` and confirm fully cited claims pass while duplicate claims, malformed or repeated references, unknown citations, insufficient coverage, and invalid policies fail.
