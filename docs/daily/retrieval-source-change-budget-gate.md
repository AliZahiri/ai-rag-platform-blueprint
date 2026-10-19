# Add retrieval source change budget gate

<!-- daily-pr-task: retrieval-source-change-budget-gate -->

A RAG index can be technically healthy while an unexpectedly large corpus update changes answer behavior. This offline gate compares approved and candidate source manifests by stable source ID and digest. It rejects duplicate or malformed evidence, calculates additions, removals, and changed sources, and requires an explicit approval reference when the configured change budget is exceeded. It does not fetch source content or call a provider.

## Portfolio Value

Makes corpus rollout risk reviewable by detecting unexpectedly large retrieval-source changes before an index promotion changes answer behavior.

## Validation

Run python3 -m unittest discover -s tests and confirm a small digest change passes, a change above the configured budget needs an approval reference, and malformed manifest evidence is rejected.
