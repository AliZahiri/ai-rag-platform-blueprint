from __future__ import annotations

from datetime import date

from scripts.citation_source_ids import citation_source_warnings
from scripts.source_freshness_policy import source_freshness_warnings


def citation_freshness_violations(sources: list[dict[str, object]], *, today: date, max_age_days: int = 180) -> tuple[str, ...]:
    if max_age_days <= 0:
        raise ValueError("maximum source age must be positive")
    violations: list[str] = []
    if not sources:
        violations.append("at_least_one_citation_source_is_required")
    violations.extend(citation_source_warnings(sources))
    for index, source in enumerate(sources):
        source_id = str(source.get("source_id", "")).strip() or f"source_{index}"
        violations.extend(f"{source_id}:{warning}" for warning in source_freshness_warnings(source, today=today, max_age_days=max_age_days))
    return tuple(violations)


def citations_are_fresh_for_release(sources: list[dict[str, object]], *, today: date, max_age_days: int = 180) -> bool:
    return not citation_freshness_violations(sources, today=today, max_age_days=max_age_days)
