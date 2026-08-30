from __future__ import annotations

from math import isfinite


def answer_decision_violations(evidence: dict[str, object], *, minimum_retrieval_confidence: float = 0.65, minimum_groundedness: float = 0.80) -> tuple[str, ...]:
    for name, value in (("minimum_retrieval_confidence", minimum_retrieval_confidence), ("minimum_groundedness", minimum_groundedness)):
        if not _probability(value):
            raise ValueError(f"{name} must be a probability")
    violations: list[str] = []
    if not isinstance(evidence.get("query_id"), str) or not evidence["query_id"].strip():
        violations.append("query_id_is_required")
    decision = evidence.get("decision")
    if decision not in {"answer", "abstain"}:
        violations.append("decision_must_be_answer_or_abstain")
    retrieval_confidence = evidence.get("retrieval_confidence")
    groundedness = evidence.get("groundedness")
    if not _probability(retrieval_confidence):
        violations.append("retrieval_confidence_must_be_a_probability")
    if not _probability(groundedness):
        violations.append("groundedness_must_be_a_probability")
    citation_count = evidence.get("citation_count")
    if not isinstance(citation_count, int) or isinstance(citation_count, bool) or citation_count < 0:
        violations.append("citation_count_must_be_a_non_negative_integer")
    if decision == "answer":
        if _probability(retrieval_confidence) and retrieval_confidence < minimum_retrieval_confidence:
            violations.append("answer_retrieval_confidence_is_below_policy")
        if _probability(groundedness) and groundedness < minimum_groundedness:
            violations.append("answer_groundedness_is_below_policy")
        if isinstance(citation_count, int) and not isinstance(citation_count, bool) and citation_count == 0:
            violations.append("answer_requires_at_least_one_citation")
    if decision == "abstain" and (not isinstance(evidence.get("reason"), str) or not evidence["reason"].strip()):
        violations.append("abstention_reason_is_required")
    return tuple(violations)


def answer_decision_is_safe(evidence: dict[str, object], **policy: object) -> bool:
    return not answer_decision_violations(evidence, **policy)


def _probability(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and isfinite(float(value)) and 0 <= value <= 1
