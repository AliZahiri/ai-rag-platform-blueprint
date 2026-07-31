# Add embedding dimension compatibility contract

<!-- daily-pr-task: embedding-dimension-contract -->

Changing an embedding model without verifying its vector size can make an existing index unreadable or silently route writes to an incompatible collection. This offline contract validates unique route identities, non-empty provider and model metadata, positive integer dimensions, and exact agreement between model output and vector-index dimensions. It performs no provider calls and is safe for default CI.

## Portfolio Value

Prevents incompatible embedding migrations from corrupting retrieval paths by making model-to-index vector dimensions explicit, deterministic, and reviewable without live provider access.

## Validation

Run `python3 -m unittest discover -s tests` and confirm compatible bindings pass while empty configuration, missing metadata, duplicate routes, invalid dimensions, and model/index mismatches fail.
