# Add provider retry budget evidence gate

<!-- daily-pr-task: provider-retry-budget-evidence-gate -->

Provider throttling and transient failures must not turn one LLM request into an unbounded retry storm. This offline gate validates sequential attempts for one request, retryable status classes, non-negative backoff, and explicit attempt and cumulative-delay budgets without making paid provider calls.

## Portfolio Value

Adds deterministic retry-storm protection and provider-fallback evidence while keeping default CI offline and free of paid model calls.

## Validation

Run python3 -m unittest discover -s tests and confirm bounded retryable failures pass while mixed request IDs, invalid sequences, non-retryable retries, excessive attempts or delay, malformed evidence, and invalid policy fail.
