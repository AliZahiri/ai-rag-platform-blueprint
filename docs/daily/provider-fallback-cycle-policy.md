# Add provider fallback cycle policy

<!-- daily-pr-task: provider-fallback-cycle-policy -->

Provider fallback policy should validate model aliases before live traffic. Fallback chains must reference known aliases and must not create cycles.

Validation checks:

- every alias has a deployment
- fallback targets exist
- fallback graph has no cycles
- primary route is declared

## Portfolio Value

Shows multi-provider routing avoids dangling aliases and fallback loops before traffic is accepted.

## Validation

Run the unit test and confirm fallback cycles and unknown aliases are reported.
