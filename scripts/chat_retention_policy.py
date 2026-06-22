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


def retention_policy_warnings(policy: dict[str, object]) -> tuple[str, ...]:
    warnings: list[str] = []
    for field in ("user_history_days", "operational_log_days", "backup_retention_days"):
        value = policy.get(field)
        if not isinstance(value, int) or value <= 0:
            warnings.append(f"{field}_must_be_positive_days")

    if not isinstance(policy.get("anonymization_required"), bool):
        warnings.append("anonymization_required_must_be_boolean")

    support_scope = policy.get("support_access_scope")
    if not isinstance(support_scope, str) or not support_scope.strip():
        warnings.append("support_access_scope_must_be_defined")

    return tuple(warnings)


def retention_policy_is_reviewable(policy: dict[str, object]) -> bool:
    return not missing_retention_fields(policy) and not retention_policy_warnings(policy)
