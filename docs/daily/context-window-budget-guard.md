# Add RAG context window budget guard

<!-- daily-pr-task: context-window-budget-guard -->

RAG retrieval should reserve enough context for system instructions and the generated answer before chunks are sent to a model. A deterministic budget guard keeps retrieval from silently overflowing a model route context window.

Guard inputs:

- estimated tokens per retrieved chunk
- route context budget
- reserved response tokens
- clear warnings for invalid or oversized inputs

## Portfolio Value

Makes the RAG blueprint demonstrate a concrete control for route context limits and answer quality.

## Validation

Run `python3 -m unittest discover -s tests` and confirm oversized retrieval context is rejected.
