# Add provider data residency contract gate

<!-- daily-pr-task: rag-provider-data-residency-gate -->

A provider capability match is not sufficient when a RAG request can cross an unapproved data boundary. This offline gate validates provider identifiers, approved regions, bounded retention, disabled training use, and fresh contract-review evidence. It validates declared metadata only and never sends prompts, source documents, or credentials to a provider.

## Portfolio Value

Adds a concrete privacy and residency control for multi-provider RAG platforms without introducing paid or live provider calls into CI.

## Validation

Run python3 -m unittest discover -s tests and confirm only recent no-training provider contracts in approved regions and retention bounds pass.
