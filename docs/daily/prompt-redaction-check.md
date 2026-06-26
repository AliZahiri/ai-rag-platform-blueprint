# Add prompt redaction check

<!-- daily-pr-task: prompt-redaction-check -->

Prompt redaction should run before user content is sent to external model providers. The first pass can flag obvious email, phone, and national identifier patterns for masking or manual review.

Guardrail outputs:

- detected sensitive fields
- redaction required flag
- safe-to-send decision for provider routing

## Portfolio Value

Shows privacy-aware controls for AI prompts before provider calls.

## Validation

Run the unit test and confirm common sensitive values are detected.
