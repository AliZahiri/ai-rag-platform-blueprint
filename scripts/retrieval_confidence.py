from __future__ import annotations

from math import isfinite


def _is_probability(value: object) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and isfinite(float(value))
        and 0 <= float(value) <= 1
    )


def low_confidence_source_ids(results: list[dict[str, object]], *, minimum_score: float) -> tuple[str, ...]:
    if not _is_probability(minimum_score):
        raise ValueError("minimum score must be between 0 and 1")
    low_confidence: list[str] = []
    for result in results:
        score = result.get("score")
        source_id = str(result.get("source_id", "")).strip()
        if not _is_probability(score) or float(score) < float(minimum_score):
            low_confidence.append(source_id or "unknown")
    return tuple(low_confidence)


def retrieval_meets_confidence_threshold(results: list[dict[str, object]], *, minimum_score: float) -> bool:
    return bool(results) and not low_confidence_source_ids(results, minimum_score=minimum_score)
