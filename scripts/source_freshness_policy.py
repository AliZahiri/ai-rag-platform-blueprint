from __future__ import annotations

from datetime import date


def source_freshness_warnings(source: dict[str, object], *, today: date, max_age_days: int = 180) -> tuple[str, ...]:
    if not isinstance(max_age_days, int) or isinstance(max_age_days, bool) or max_age_days <= 0:
        raise ValueError("maximum source age must be a positive integer")
    warnings: list[str] = []
    status = source.get("status")
    if status not in {"valid", "amended", "review_required"}:
        warnings.append("source_status_unknown")
    reviewed_at = source.get("last_reviewed_at")
    if not isinstance(reviewed_at, date):
        warnings.append("last_reviewed_at_missing")
        return tuple(warnings)
    age_days = (today - reviewed_at).days
    if age_days < 0:
        warnings.append("source_review_is_in_future")
    elif age_days > max_age_days:
        warnings.append("source_review_is_stale")
    return tuple(warnings)


def source_is_fresh(source: dict[str, object], *, today: date, max_age_days: int = 180) -> bool:
    return not source_freshness_warnings(source, today=today, max_age_days=max_age_days)
