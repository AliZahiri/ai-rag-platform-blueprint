from __future__ import annotations


def citation_policy_warnings(answer_plan: dict[str, object], *, min_citations: int = 1) -> tuple[str, ...]:
    warnings: list[str] = []
    mode = answer_plan.get("mode")
    citation_count = answer_plan.get("citation_count", 0)
    if mode not in {"source_backed", "general_guidance", "clarifying_question"}:
        warnings.append("answer_mode_must_be_declared")
    if mode == "source_backed":
        if not isinstance(citation_count, int) or citation_count < min_citations:
            warnings.append("source_backed_answer_needs_citations")
    return tuple(warnings)


def citation_policy_is_satisfied(answer_plan: dict[str, object], *, min_citations: int = 1) -> bool:
    return not citation_policy_warnings(answer_plan, min_citations=min_citations)
