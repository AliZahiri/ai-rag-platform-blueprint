from __future__ import annotations

from math import isfinite


def retrieval_rerank_violations(candidates: list[dict[str, object]], results: list[dict[str, object]], *, minimum_score: float = 0.0, maximum_results: int = 20) -> tuple[str, ...]:
    if not isinstance(minimum_score, (int, float)) or isinstance(minimum_score, bool) or not isfinite(float(minimum_score)):
        raise ValueError("minimum score must be finite")
    if not isinstance(maximum_results, int) or isinstance(maximum_results, bool) or maximum_results <= 0:
        raise ValueError("maximum results must be a positive integer")
    if not candidates:
        return ("at_least_one_candidate_is_required",)

    violations: list[str] = []
    candidate_ids: set[str] = set()
    for position, candidate in enumerate(candidates):
        chunk_id = str(candidate.get("chunk_id", "")).strip()
        if not chunk_id:
            violations.append(f"candidate_{position}:chunk_id_is_required")
        elif chunk_id in candidate_ids:
            violations.append(f"candidate_{position}:chunk_id_must_be_unique")
        candidate_ids.add(chunk_id)

    if not results:
        violations.append("at_least_one_rerank_result_is_required")
        return tuple(violations)
    if len(results) > min(maximum_results, len(candidates)):
        violations.append("rerank_result_count_exceeds_limit")

    seen_results: set[str] = set()
    previous_score: float | None = None
    for position, result in enumerate(results):
        chunk_id = str(result.get("chunk_id", "")).strip()
        if not chunk_id:
            violations.append(f"result_{position}:chunk_id_is_required")
        elif chunk_id not in candidate_ids:
            violations.append(f"result_{position}:chunk_id_is_not_a_candidate")
        elif chunk_id in seen_results:
            violations.append(f"result_{position}:chunk_id_must_be_unique")
        seen_results.add(chunk_id)
        if result.get("rank") != position + 1:
            violations.append(f"result_{position}:rank_must_be_contiguous")
        score = result.get("score")
        if not isinstance(score, (int, float)) or isinstance(score, bool) or not isfinite(float(score)):
            violations.append(f"result_{position}:score_must_be_finite")
            continue
        numeric_score = float(score)
        if numeric_score < minimum_score:
            violations.append(f"result_{position}:score_below_minimum")
        if previous_score is not None and numeric_score > previous_score:
            violations.append(f"result_{position}:score_order_is_not_descending")
        previous_score = numeric_score
    return tuple(violations)


def retrieval_rerank_is_valid(candidates: list[dict[str, object]], results: list[dict[str, object]], **policy: object) -> bool:
    return not retrieval_rerank_violations(candidates, results, **policy)
