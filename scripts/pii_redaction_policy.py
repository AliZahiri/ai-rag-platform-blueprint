from __future__ import annotations

REQUIRED_PII_CATEGORIES = ("phone", "national_id", "bank_card", "address", "case_tracking_number")


def missing_redaction_categories(configured_categories: set[str]) -> tuple[str, ...]:
    return tuple(category for category in REQUIRED_PII_CATEGORIES if category not in configured_categories)


def redaction_coverage_is_complete(configured_categories: set[str]) -> bool:
    return not missing_redaction_categories(configured_categories)
