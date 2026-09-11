from __future__ import annotations

from math import isfinite

REQUIRED_PROVIDER_BUDGET_FIELDS = (
    "provider",
    "daily_cap_usd",
    "monthly_cap_usd",
    "alert_threshold_pct",
    "owner",
)


def _is_finite_number(value: object) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and (not isinstance(value, float) or isfinite(value))
    )


def provider_budget_warnings(policy: dict[str, object]) -> tuple[str, ...]:
    warnings: list[str] = []
    for field in REQUIRED_PROVIDER_BUDGET_FIELDS:
        if field not in policy:
            warnings.append(f"{field}_missing")

    daily_cap = policy.get("daily_cap_usd")
    monthly_cap = policy.get("monthly_cap_usd")
    threshold = policy.get("alert_threshold_pct")

    daily_cap_is_valid = _is_finite_number(daily_cap) and daily_cap > 0
    monthly_cap_is_valid = _is_finite_number(monthly_cap) and monthly_cap > 0

    if not daily_cap_is_valid:
        warnings.append("daily_cap_usd_must_be_positive")
    if not monthly_cap_is_valid:
        warnings.append("monthly_cap_usd_must_be_positive")
    if daily_cap_is_valid and monthly_cap_is_valid and monthly_cap < daily_cap:
        warnings.append("monthly_cap_usd_must_cover_daily_cap")
    if not _is_finite_number(threshold) or not 1 <= threshold <= 100:
        warnings.append("alert_threshold_pct_must_be_1_to_100")

    return tuple(warnings)


def provider_budget_is_safe(policy: dict[str, object]) -> bool:
    return not provider_budget_warnings(policy)
