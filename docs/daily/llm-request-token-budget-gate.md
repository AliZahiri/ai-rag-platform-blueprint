# Add LLM request token budget gate

<!-- daily-pr-task: llm-request-token-budget-gate -->

Model route budgets should be enforced before a request reaches a provider. This offline gate validates a request's input, reserved output, and total-token limits against a declared route capacity. It makes no provider call and is intended for admission control or CI policy checks.

## Portfolio Value

Demonstrates deterministic admission control for LLM context and output reservations before cost or latency reaches an external provider.

## Validation

Run `python3 -m unittest discover -s tests` and confirm valid requests pass while non-positive token values, context-window overflow, and route-budget overflow fail.
