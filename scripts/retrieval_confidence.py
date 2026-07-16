from __future__ import annotations


def low_confidence_source_ids(results: list[dict[str, object]], *, minimum_score: float) -> tuple[str, ...]:
    if not 0 <= minimum_score <= 1:
        raise ValueError("minimum score must be between 0 and 1")
    low_confidence: list[str] = []
    for result in results:
        score = result.get("score")
        source_id = str(result.get("source_id", "")).strip()
        if not isinstance(score, (int, float)) or score < minimum_score:
            low_confidence.append(source_id or "unknown")
    return tuple(low_confidence)


def retrieval_meets_confidence_threshold(results: list[dict[str, object]], *, minimum_score: float) -> bool:
    return bool(results) and not low_confidence_source_ids(results, minimum_score=minimum_score)
