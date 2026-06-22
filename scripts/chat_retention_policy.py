from __future__ import annotations

REQUIRED_RETENTION_FIELDS = (
    "user_history_days",
    "operational_log_days",
    "anonymization_required",
    "backup_retention_days",
    "support_access_scope",
)


def missing_retention_fields(policy: dict[str, object]) -> tuple[str, ...]:
    return tuple(field for field in REQUIRED_RETENTION_FIELDS if field not in policy)


def retention_policy_is_reviewable(policy: dict[str, object]) -> bool:
    return not missing_retention_fields(policy)
