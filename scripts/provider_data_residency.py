from __future__ import annotations

from datetime import datetime


def provider_data_residency_violations(providers: list[dict[str, object]], *, allowed_regions: tuple[str, ...], now: datetime, maximum_retention_days: int = 30, maximum_review_age_days: int = 365) -> tuple[str, ...]:
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("current time must be timezone-aware")
    normalized_regions = {region.strip().lower() for region in allowed_regions if isinstance(region, str) and region.strip()}
    if not normalized_regions:
        raise ValueError("allowed regions must contain non-empty strings")
    if not isinstance(maximum_retention_days, int) or isinstance(maximum_retention_days, bool) or maximum_retention_days < 0:
        raise ValueError("maximum retention days must be non-negative")
    if not isinstance(maximum_review_age_days, int) or isinstance(maximum_review_age_days, bool) or maximum_review_age_days < 1:
        raise ValueError("maximum review age must be a positive integer")
    if not isinstance(providers, list) or not providers:
        return ("at_least_one_provider_contract_is_required",)

    violations: list[str] = []
    seen_provider_ids: set[str] = set()
    for index, provider in enumerate(providers):
        if not isinstance(provider, dict):
            violations.append(f"provider_{index}:must_be_an_object")
            continue
        provider_id = provider.get("provider_id")
        if not isinstance(provider_id, str) or not provider_id.strip():
            violations.append(f"provider_{index}:provider_id_is_required")
        elif provider_id in seen_provider_ids:
            violations.append(f"provider_{index}:provider_id_must_be_unique")
        else:
            seen_provider_ids.add(provider_id)
        region = provider.get("region")
        if not isinstance(region, str) or region.strip().lower() not in normalized_regions:
            violations.append(f"provider_{index}:region_is_not_approved")
        retention_days = provider.get("retention_days")
        if not isinstance(retention_days, int) or isinstance(retention_days, bool) or retention_days < 0 or retention_days > maximum_retention_days:
            violations.append(f"provider_{index}:retention_days_exceed_policy")
        if provider.get("training_use_permitted") is not False:
            violations.append(f"provider_{index}:training_use_must_be_disabled")
        reviewed_at = _timestamp(provider.get("contract_reviewed_at"))
        if reviewed_at is None:
            violations.append(f"provider_{index}:contract_reviewed_at_must_be_timezone_aware")
        elif not 0 <= (now - reviewed_at).total_seconds() <= maximum_review_age_days * 86400:
            violations.append(f"provider_{index}:contract_review_is_stale_or_future_dated")
    return tuple(violations)


def provider_data_residency_is_approved(providers: list[dict[str, object]], **policy: object) -> bool:
    return not provider_data_residency_violations(providers, **policy)


def _timestamp(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None and parsed.utcoffset() is not None else None
