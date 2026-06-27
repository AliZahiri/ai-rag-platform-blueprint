# Add model fallback budget policy

<!-- daily-pr-task: model-fallback-budget-policy -->

Fallback routing should consider reliability and spend together. A fallback model is only useful if it stays inside the request budget and preserves the required capabilities.

Policy checks:

- fallback model alias is defined
- estimated cost stays within request budget
- fallback preserves required capabilities
- retry count is bounded

## Portfolio Value

Shows model fallback is controlled by spend and reliability policy instead of blind retries.

## Validation

Run the unit test and confirm fallback candidates are rejected when they exceed budget.
