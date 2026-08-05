# Add retrieval prompt injection evidence gate

<!-- daily-pr-task: retrieval-prompt-injection-evidence-gate -->

Retrieved text is untrusted data and can contain instruction-like content that attempts to override the system prompt. This offline gate validates unique chunk identities and requires untrusted chunks with detected instruction signals to be quarantined and excluded from model context. It consumes scanner metadata only and does not call an LLM or inspect private content in CI.

## Portfolio Value

Adds a deterministic trust-boundary control between retrieval and prompting so instruction-bearing external evidence cannot silently become executable model context.

## Validation

Run `python3 -m unittest discover -s tests` and confirm clean or correctly quarantined chunks pass while empty input, duplicate identities, invalid trust metadata, invalid signal counts, and uncontained instruction signals fail.
