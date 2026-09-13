# Add RAG evaluation cohort evidence gate

<!-- daily-pr-task: rag-evaluation-cohort-evidence-gate -->

RAG quality claims need a bounded, identifiable evaluation cohort. This offline gate checks that a completed evaluation reports the approved dataset, enough queries, citation precision, and fresh evidence. It validates summary metadata only and makes no provider calls.

## Portfolio Value

Makes retrieval-quality assertions depend on a fresh, approved evaluation cohort rather than an unscoped aggregate metric.

## Validation

Run python3 -m unittest discover -s tests and confirm only a fresh completed evaluation of the approved cohort with adequate coverage and citation precision passes.
