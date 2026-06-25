# Add retrieval threshold policy

<!-- daily-pr-task: retrieval-threshold-policy -->

Retrieval policies should define how many chunks can enter the prompt and what minimum similarity score is acceptable. This keeps low-confidence context from silently shaping model answers.

Policy inputs:

- minimum similarity score
- maximum retrieved chunks
- empty retrieval behavior
- owner for threshold review

## Portfolio Value

Adds measurable RAG quality controls around retrieval score and chunk count.

## Validation

Run the unit test and confirm unsafe retrieval thresholds are reported.
