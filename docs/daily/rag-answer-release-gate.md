# Add RAG answer release gate

<!-- daily-pr-task: rag-answer-release-gate -->

A grounded answer should not be released when retrieval confidence, evidence coverage, or source diversity fails independently. This aggregate gate reuses the existing deterministic policies and returns named violations suitable for API responses, evaluation reports, and CI fixtures without invoking an LLM provider.

## Portfolio Value

Connects individual RAG quality validators into a release decision that can block weak or partially grounded answers.

## Validation

Run `python3 -m unittest discover -s tests` and confirm a confident, diverse, fully evidenced answer passes while combined quality failures remain observable.
