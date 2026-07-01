# Add RAG context budget policy

<!-- daily-pr-task: rag-context-budget-policy -->

RAG context budget policy should keep retrieved chunks, system prompt, and answer space inside the model context window. This prevents silent truncation and expensive low-quality answers.

Budget fields:

- context window tokens
- prompt tokens
- retrieved chunk tokens
- reserved answer tokens
- safety margin tokens

## Portfolio Value

Shows answer quality is protected by explicit prompt, retrieval, and answer token budgets.

## Validation

Run the unit test and confirm over-budget retrieval plans are rejected.
