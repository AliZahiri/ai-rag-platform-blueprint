# Add RAG evaluation leakage evidence gate

<!-- daily-pr-task: rag-evaluation-leakage-evidence-gate -->

Evaluation results are misleading when hashed source identities or case identities overlap between tuning and holdout sets. This offline gate requires unique opaque identifiers, a minimum holdout size, and zero train/holdout overlap without storing prompts, answers, source content, or personal data.

## Portfolio Value

Adds deterministic holdout-isolation evidence so apparent RAG quality improvements cannot be attributed to tuning/evaluation data leakage.

## Validation

Run python3 -m unittest discover -s tests and confirm disjoint opaque identifiers pass while overlap, duplicates, malformed identifiers, undersized holdouts, and invalid policy fail.
