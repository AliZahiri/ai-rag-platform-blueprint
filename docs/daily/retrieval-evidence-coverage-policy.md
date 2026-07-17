# Add retrieval evidence coverage policy

<!-- daily-pr-task: retrieval-evidence-coverage-policy -->

Grounded answers should expose which factual claim identifiers are supported by retrieved evidence. The policy rejects missing or blank evidence mappings so an evaluation gate can distinguish fully cited answers from partially grounded output.

## Portfolio Value

Adds a deterministic citation completeness gate that can be used by RAG evaluation and release checks.

## Validation

Run `python3 -m unittest discover -s tests` and confirm claims without evidence are reported.
