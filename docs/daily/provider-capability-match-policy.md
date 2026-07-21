# Add provider capability match policy

<!-- daily-pr-task: provider-capability-match-policy -->

A model route should be selected only when its declared provider capabilities satisfy the workload contract. The policy checks required boolean capabilities and the minimum context window locally so unsupported JSON, tool, vision, or long-context workloads fail before a paid request is attempted.

## Portfolio Value

Makes provider routing auditable and prevents capability or context-window mismatches without requiring live API access in CI.

## Validation

Run `python3 -m unittest discover -s tests` and confirm missing capabilities and insufficient context windows block provider selection.
