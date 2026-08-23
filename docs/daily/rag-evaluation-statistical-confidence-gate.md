# Add RAG evaluation statistical confidence gate

<!-- daily-pr-task: rag-evaluation-statistical-confidence-gate -->

Release evaluation should not pass on a high point estimate backed by too few samples. This offline gate requires a versioned dataset, a minimum sample count, a declared confidence level, a lower confidence bound above policy, and timezone-aware evaluation evidence.

## Portfolio Value

Makes RAG quality promotion depend on sample size and a conservative confidence bound rather than an easily misleading point score.

## Validation

Run python3 -m unittest discover -s tests and confirm weak, undersampled, naive-timestamped, or invalid evaluation evidence fails deterministically.
