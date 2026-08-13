# Add response PII redaction evidence gate

<!-- daily-pr-task: response-pii-redaction-evidence-gate -->

Prompt filtering alone cannot prevent sensitive data from reaching a user through a generated answer. This offline release gate binds a response scan report to the exact response digest, requires a fresh detector observation, and blocks delivery whenever the final response still matches a configured PII detector. It reuses local detection rules and makes no model or provider calls.

## Portfolio Value

Extends AI safety controls from prompt intake to the final answer, using traceable and fresh evidence rather than an unverified claim that redaction occurred.

## Validation

Run `python3 -m unittest discover -s tests` and confirm fresh clean response evidence passes while digest mismatches, stale or naive timestamps, detector-report mismatches, PII-bearing responses, unsafe release decisions, and invalid policy values fail.
