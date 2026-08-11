# Add prompt template version contract

<!-- daily-pr-task: prompt-template-version-contract -->

Prompt changes should be traceable and reviewable before they reach a production model route. This offline gate validates template metadata: a stable template identifier, semantic version, immutable SHA-256 content digest, explicit approved state, and a timezone-aware review timestamp. It never sends a prompt to a provider.

## Portfolio Value

Adds change-control evidence for prompt behavior, complementing the repository's existing safety, cost, and retrieval release gates.

## Validation

Run `python3 -m unittest discover -s tests` and confirm approved immutable prompt metadata passes while unstable IDs, non-semantic versions, invalid digests, unapproved templates, and naive review timestamps fail.
