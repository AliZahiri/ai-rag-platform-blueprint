from __future__ import annotations

REQUIRED_PROVIDER_BUDGET_FIELDS = (
    "provider",
    "daily_cap_usd",
    "monthly_cap_usd",
    "alert_threshold_pct",
    "owner",
)


def provider_budget_warnings(policy: dict[str, object]) -> tuple[str, ...]:
    warnings: list[str] = []
    for field in REQUIRED_PROVIDER_BUDGET_FIELDS:
        if field not in policy:
            warnings.append(f"{field}_missing")

    daily_cap = policy.get("daily_cap_usd")
    monthly_cap = policy.get("monthly_cap_usd")
    threshold = policy.get("alert_threshold_pct")

    if not isinstance(daily_cap, (int, float)) or daily_cap <= 0:
        warnings.append("daily_cap_usd_must_be_positive")
    if not isinstance(monthly_cap, (int, float)) or monthly_cap <= 0:
        warnings.append("monthly_cap_usd_must_be_positive")
    if isinstance(daily_cap, (int, float)) and isinstance(monthly_cap, (int, float)) and monthly_cap < daily_cap:
        warnings.append("monthly_cap_usd_must_cover_daily_cap")
    if not isinstance(threshold, (int, float)) or not 1 <= threshold <= 100:
        warnings.append("alert_threshold_pct_must_be_1_to_100")

    return tuple(warnings)


def provider_budget_is_safe(policy: dict[str, object]) -> bool:
    return not provider_budget_warnings(policy)
