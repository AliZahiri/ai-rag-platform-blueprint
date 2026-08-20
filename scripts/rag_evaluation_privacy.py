from __future__ import annotations

from datetime import date, datetime, timedelta, timezone


def evaluation_privacy_violations(
    evidence: dict[str, object], *, today: date, max_review_age_days: int = 90
) -> tuple[str, ...]:
    violations: list[str] = []
    if not isinstance(max_review_age_days, int) or isinstance(max_review_age_days, bool) or max_review_age_days < 1:
        return ("max_review_age_days_must_be_positive",)
    for field in ("dataset_id", "approved_by"):
        if not isinstance(evidence.get(field), str) or not evidence[field].strip():
            violations.append(f"{field}_is_required")
    if evidence.get("pii_scan_passed") is not True:
        violations.append("pii_scan_must_pass")
    if evidence.get("redaction_verified") is not True:
        violations.append("redaction_must_be_verified")
    reviewed_at = _parse_date(evidence.get("reviewed_at"))
    if reviewed_at is None:
        violations.append("reviewed_at_must_be_an_iso_date")
    elif reviewed_at > today:
        violations.append("reviewed_at_cannot_be_in_the_future")
    elif reviewed_at < today - timedelta(days=max_review_age_days):
        violations.append("privacy_review_is_stale")
    return tuple(violations)


def evaluation_privacy_is_approved(
    evidence: dict[str, object], *, today: date, max_review_age_days: int = 90
) -> bool:
    return not evaluation_privacy_violations(evidence, today=today, max_review_age_days=max_review_age_days)


def _parse_date(value: object) -> date | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc).date()
    except ValueError:
        return None
