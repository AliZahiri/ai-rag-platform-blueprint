# Add RAG evaluation slice coverage gate

<!-- daily-pr-task: rag-evaluation-slice-coverage-gate -->

Aggregate RAG scores can hide regressions in important traffic slices such as long-context, multilingual, or sparse-retrieval queries. This deterministic gate validates unique evaluation sample identifiers, rejects undeclared slices, and requires a minimum sample count for every declared slice before a release report is trusted. It operates on offline evaluation metadata and never calls a model provider.

## Portfolio Value

Prevents aggregate RAG metrics from masking untested query classes by requiring deterministic, reviewable coverage of every declared evaluation slice.

## Validation

Run `python3 -m unittest discover -s tests` and confirm complete slice coverage passes while duplicate sample IDs, missing metadata, undeclared slices, insufficient coverage, and invalid policy values fail.
