from __future__ import annotations


_ALLOWED = {"safe", "review", "blocked"}


def response_safety_classification_violations(records: list[dict[str, object]], *, minimum_safe_confidence: float = 0.8) -> tuple[str, ...]:
    if not isinstance(minimum_safe_confidence, (int, float)) or isinstance(minimum_safe_confidence, bool) or not 0 < minimum_safe_confidence <= 1:
        raise ValueError("minimum safe confidence must be between zero and one")
    if not records:
        return ("at_least_one_response_record_is_required",)
    violations: list[str] = []
    seen_ids: set[str] = set()
    for index, record in enumerate(records):
        response_id = record.get("response_id")
        if not isinstance(response_id, str) or not response_id.strip():
            violations.append(f"record_{index}:response_id_is_required")
        elif response_id in seen_ids:
            violations.append(f"record_{index}:response_id_must_be_unique")
        seen_ids.add(response_id)
        classification = record.get("classification")
        if classification not in _ALLOWED:
            violations.append(f"record_{index}:classification_is_invalid")
        confidence = record.get("confidence")
        if not isinstance(confidence, (int, float)) or isinstance(confidence, bool) or not 0 <= confidence <= 1:
            violations.append(f"record_{index}:confidence_must_be_between_zero_and_one")
        elif classification == "safe" and confidence < minimum_safe_confidence:
            violations.append(f"record_{index}:safe_classification_confidence_is_too_low")
        if record.get("release") is not (classification == "safe"):
            violations.append(f"record_{index}:release_decision_must_match_classification")
    return tuple(violations)


def response_safety_classification_is_safe(records: list[dict[str, object]], **policy: object) -> bool:
    return not response_safety_classification_violations(records, **policy)
