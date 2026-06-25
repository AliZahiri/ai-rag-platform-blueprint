from __future__ import annotations


def retrieval_policy_warnings(policy: dict[str, object]) -> tuple[str, ...]:
    warnings: list[str] = []
    min_score = policy.get("min_similarity_score")
    max_chunks = policy.get("max_chunks")
    empty_behavior = policy.get("empty_retrieval_behavior")

    if not isinstance(min_score, (int, float)) or not 0 < min_score <= 1:
        warnings.append("min_similarity_score_must_be_between_0_and_1")
    if not isinstance(max_chunks, int) or not 1 <= max_chunks <= 20:
        warnings.append("max_chunks_must_be_between_1_and_20")
    if empty_behavior not in {"answer_without_sources", "ask_clarifying_question", "escalate"}:
        warnings.append("empty_retrieval_behavior_must_be_explicit")

    return tuple(warnings)


def retrieval_policy_is_safe(policy: dict[str, object]) -> bool:
    return not retrieval_policy_warnings(policy)
