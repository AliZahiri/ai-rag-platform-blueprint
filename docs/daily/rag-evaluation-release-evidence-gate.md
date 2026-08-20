# Add RAG evaluation release evidence gate

<!-- daily-pr-task: rag-evaluation-release-evidence -->

A RAG release should carry deterministic evidence that evaluation metrics meet declared thresholds, the evaluation dataset version is identified, and a regression review has completed. This offline gate validates supplied metadata only; it does not load customer data or call an LLM provider.

## Portfolio Value

Adds a provider-free release gate that makes RAG evaluation thresholds, data versioning, and regression review auditable before promotion.

## Validation

Run `python3 -m unittest discover -s tests` and confirm only identified, threshold-compliant, timezone-stamped, reviewed evaluation evidence passes.
