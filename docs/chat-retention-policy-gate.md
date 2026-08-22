# Chat retention policy gate

`scripts/chat_retention_policy_gate.py` validates a JSON policy before a release
or CI promotion. It performs no provider calls, does not read environment secrets,
and does not retain policy content.

## Policy contract

The policy must be a JSON object containing:

- `user_history_days`, `operational_log_days`, and `backup_retention_days` as
  positive integer day counts;
- `anonymization_required` as a boolean; and
- `support_access_scope` as a non-empty description of the access boundary.

The gate validates that the fields are explicit. It does not choose retention
periods for an organization; those remain a legal, privacy, and operational
decision.

## Run locally or in CI

```bash
python3 scripts/chat_retention_policy_gate.py retention-policy.json
```

It writes exactly one JSON document to standard output and exits `0` only when
the policy is reviewable. An unreadable, malformed, incomplete, or unsafe policy
exits `1`. For example:

```json
{"missing_fields": [], "ok": true, "warnings": []}
```

Use the exit status as a release gate and archive the JSON report as CI evidence;
do not put customer histories, tokens, or private policy data in the repository.
