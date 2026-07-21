# Add citation span integrity policy

<!-- daily-pr-task: citation-span-integrity-policy -->

Generated answers can cite the correct source identifier while quoting the wrong byte range. This policy validates bounded citation offsets, non-empty source identifiers, and exact quote-to-source matches before citation metadata is exposed to users. The check is deterministic and requires no provider calls.

## Portfolio Value

Adds a testable traceability control that prevents stale or malformed citation offsets from misrepresenting retrieved evidence.

## Validation

Run `python3 -m unittest discover -s tests` and confirm exact spans pass while quote mismatches and invalid bounds are rejected.
