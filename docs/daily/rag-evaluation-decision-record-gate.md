# Add RAG evaluation decision record gate

<!-- daily-pr-task: rag-evaluation-decision-record-gate -->

A release decision should be reproducible from an explicit comparison record, rather than inferred from a dashboard screenshot. This offline gate checks that a baseline and candidate are distinct, the decision is explicit, the required reviewers are recorded as opaque identifiers, and every declared metric stays within its approved regression budget. It processes aggregate evidence only; prompts, answers, and provider credentials are out of scope.

## Portfolio Value

Makes RAG release decisions auditable and bounded by explicit evaluation-regression budgets without storing model inputs or requiring paid provider calls.

## Validation

Run python3 -m unittest discover -s tests and confirm only distinct, explicitly decided, independently reviewed records whose metrics stay inside regression budgets pass.
