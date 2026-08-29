# Add RAG trace continuity evidence gate

<!-- daily-pr-task: rag-trace-continuity-evidence-gate -->

A RAG response should be traceable across retrieval, generation, and citation assembly. This offline gate validates supplied span metadata: one shared trace identity, unique span identities, required stage coverage, successful status, and an explicit retrieval-to-generation-to-citation parent chain. It does not export prompts, retrieved text, or customer data.

## Portfolio Value

Connects retrieval, model, and citation observability into deterministic trace evidence while keeping prompts and source content out of CI artifacts.

## Validation

Run python3 -m unittest discover -s tests and confirm missing stages, duplicate spans, cross-trace metadata, failed status, or broken parent relationships fail.
