# Add PII redaction coverage policy

<!-- daily-pr-task: pii-redaction-coverage-policy -->

PII redaction coverage policy should verify that provider-bound prompts have masking rules for the most sensitive categories.

Required categories:

- phone
- national id
- bank card
- address
- case tracking number

## Portfolio Value

Shows AI gateway safety includes privacy coverage before prompts leave the platform.

## Validation

Run the unit test and confirm required PII categories are covered.
