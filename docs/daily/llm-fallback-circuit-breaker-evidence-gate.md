# Add LLM fallback circuit breaker evidence gate

<!-- daily-pr-task: llm-fallback-circuit-breaker-evidence-gate -->

Provider fallback should carry circuit-breaker evidence so a failing route is isolated without exhausting every request. This offline contract validates thresholds, state consistency, retry timing, a fallback route, and timezone-aware observations without probing a paid provider.

## Portfolio Value

Adds deterministic failure-isolation evidence to the existing route and fallback controls without requiring live or paid provider calls in CI.

## Validation

Run python3 -m unittest discover -s tests and confirm inconsistent breaker state, missing retry timing, or missing fallback evidence fails.
