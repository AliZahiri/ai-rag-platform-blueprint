from __future__ import annotations

from scripts.retrieval_confidence import low_confidence_source_ids
from scripts.retrieval_domain_diversity import retrieval_has_domain_diversity
from scripts.retrieval_evidence_coverage import uncovered_claim_ids


def answer_release_violations(*, results: list[dict[str, object]], claim_ids: list[str] | tuple[str, ...], evidence_by_claim: dict[str, list[str]], minimum_score: float, minimum_domains: int) -> tuple[str, ...]:
    violations: list[str] = []
    low_confidence = low_confidence_source_ids(results, minimum_score=minimum_score)
    if not results:
        violations.append("retrieval_results_are_required")
    elif low_confidence:
        violations.append("retrieval_confidence_gate_failed:" + ",".join(low_confidence))
    uncovered = uncovered_claim_ids(claim_ids, evidence_by_claim)
    if not claim_ids:
        violations.append("claim_identifiers_are_required")
    elif uncovered:
        violations.append("evidence_coverage_gate_failed:" + ",".join(uncovered))
    if not retrieval_has_domain_diversity(results, minimum_domains=minimum_domains):
        violations.append("retrieval_domain_diversity_gate_failed")
    return tuple(violations)


def answer_is_releasable(**inputs: object) -> bool:
    return not answer_release_violations(**inputs)
