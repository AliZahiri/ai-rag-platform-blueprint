# Add RAG answer citation policy

<!-- daily-pr-task: rag-answer-citation-policy -->

RAG answers should clearly indicate when a response is backed by retrieved sources. Citation policy keeps the answer contract explicit and helps reviewers spot unsupported responses.

Policy checks:

- answer mode is declared
- source-backed answers include citation count
- minimum citation count is met
- unsupported answers are labeled clearly

## Portfolio Value

Shows generated answers are tied back to retrieved evidence instead of unsupported model output.

## Validation

Run the unit test and confirm answer plans require citations when source-backed answers are expected.
