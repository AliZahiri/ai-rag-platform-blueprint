from __future__ import annotations

from datetime import datetime


def _timestamp(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None and parsed.utcoffset() is not None else None


def evaluation_dataset_provenance_violations(cases: list[dict[str, object]], *, now: datetime, maximum_review_age_days: int = 180) -> tuple[str, ...]:
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("current time must be timezone-aware")
    if not isinstance(maximum_review_age_days, int) or isinstance(maximum_review_age_days, bool) or maximum_review_age_days <= 0:
        raise ValueError("maximum review age must be positive")
    if not cases:
        return ("at_least_one_evaluation_case_is_required",)

    violations: list[str] = []
    seen_case_ids: set[str] = set()
    for index, case in enumerate(cases):
        case_id = case.get("case_id")
        if not isinstance(case_id, str) or not case_id.strip():
            violations.append(f"case_{index}:case_id_is_required")
        elif case_id in seen_case_ids:
            violations.append(f"case_{index}:case_id_must_be_unique")
        seen_case_ids.add(case_id)
        if not isinstance(case.get("source_snapshot"), str) or not case["source_snapshot"].strip():
            violations.append(f"case_{index}:source_snapshot_is_required")
        if not isinstance(case.get("expected_answer"), str) or not case["expected_answer"].strip():
            violations.append(f"case_{index}:expected_answer_is_required")
        source_ids = case.get("source_ids")
        if not isinstance(source_ids, list) or not source_ids or not all(isinstance(source_id, str) and source_id.strip() for source_id in source_ids) or len(set(source_ids)) != len(source_ids):
            violations.append(f"case_{index}:source_ids_must_be_a_unique_non_empty_string_list")
        reviewed_at = _timestamp(case.get("reviewed_at"))
        if reviewed_at is None or (now - reviewed_at).total_seconds() < 0 or (now - reviewed_at).days > maximum_review_age_days:
            violations.append(f"case_{index}:review_is_not_within_age_budget")
    return tuple(violations)


def evaluation_dataset_provenance_is_complete(cases: list[dict[str, object]], **policy: object) -> bool:
    return not evaluation_dataset_provenance_violations(cases, **policy)
