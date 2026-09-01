from __future__ import annotations

from datetime import datetime


def deletion_propagation_violations(evidence: dict[str, object], *, maximum_propagation_seconds: int = 900) -> tuple[str, ...]:
    if not isinstance(maximum_propagation_seconds, int) or isinstance(maximum_propagation_seconds, bool) or maximum_propagation_seconds < 1:
        raise ValueError("maximum_propagation_seconds must be a positive integer")
    violations: list[str] = []
    request_id = evidence.get("request_id")
    if not isinstance(request_id, str) or not request_id.strip():
        violations.append("request_id_is_required")
    source_ids = evidence.get("source_ids")
    if not isinstance(source_ids, list) or not source_ids or any(not isinstance(item, str) or not item.strip() for item in source_ids):
        violations.append("source_ids_must_be_a_non_empty_string_list")
        expected: set[str] = set()
    else:
        expected = set(source_ids)
        if len(expected) != len(source_ids):
            violations.append("source_ids_must_be_unique")
    requested_at = _timestamp(evidence.get("requested_at"))
    if requested_at is None:
        violations.append("requested_at_must_be_timezone_aware")
    acknowledgements = evidence.get("store_acknowledgements")
    if not isinstance(acknowledgements, dict):
        violations.append("store_acknowledgements_must_be_an_object")
    else:
        for store in ("vector_index", "retrieval_cache", "serving_layer"):
            acknowledgement = acknowledgements.get(store)
            if not isinstance(acknowledgement, dict):
                violations.append(f"{store}:acknowledgement_is_required")
                continue
            deleted = acknowledgement.get("deleted_source_ids")
            if not isinstance(deleted, list) or set(deleted) != expected:
                violations.append(f"{store}:deleted_source_ids_do_not_match_request")
            completed_at = _timestamp(acknowledgement.get("completed_at"))
            if completed_at is None:
                violations.append(f"{store}:completed_at_must_be_timezone_aware")
            elif requested_at is not None and not 0 <= (completed_at - requested_at).total_seconds() <= maximum_propagation_seconds:
                violations.append(f"{store}:propagation_budget_exceeded")
    residual = evidence.get("residual_source_ids")
    if not isinstance(residual, list):
        violations.append("residual_source_ids_must_be_a_list")
    elif expected.intersection(residual):
        violations.append("deleted_sources_remain_retrievable")
    return tuple(violations)


def deletion_has_propagated(evidence: dict[str, object], **policy: object) -> bool:
    return not deletion_propagation_violations(evidence, **policy)


def _timestamp(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None and parsed.utcoffset() is not None else None
