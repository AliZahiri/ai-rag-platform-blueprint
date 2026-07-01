from __future__ import annotations


def context_budget_warnings(plan: dict[str, int]) -> tuple[str, ...]:
    warnings: list[str] = []
    required = ("context_window_tokens", "prompt_tokens", "retrieved_chunk_tokens", "reserved_answer_tokens")
    for field in required:
        if not isinstance(plan.get(field), int) or plan[field] <= 0:
            warnings.append(f"{field}_must_be_positive")
    if warnings:
        return tuple(warnings)
    safety_margin = int(plan.get("safety_margin_tokens", 512))
    total = plan["prompt_tokens"] + plan["retrieved_chunk_tokens"] + plan["reserved_answer_tokens"] + safety_margin
    if total > plan["context_window_tokens"]:
        warnings.append("context_budget_exceeds_window")
    return tuple(warnings)


def context_budget_is_safe(plan: dict[str, int]) -> bool:
    return not context_budget_warnings(plan)
