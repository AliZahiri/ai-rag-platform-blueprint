from __future__ import annotations

from math import isfinite


def claim_citation_coverage_violations(claims: list[dict[str, object]], *, known_citation_ids: set[str], minimum_coverage_ratio: float = 1.0) -> tuple[str, ...]:
    if not known_citation_ids or any(not str(value).strip() for value in known_citation_ids):
        raise ValueError("known citation ids must be non-empty")
    if not isinstance(minimum_coverage_ratio, (int, float)) or isinstance(minimum_coverage_ratio, bool) or not isfinite(float(minimum_coverage_ratio)) or not 0 <= minimum_coverage_ratio <= 1:
        raise ValueError("minimum coverage ratio must be finite and between zero and one")
    violations: list[str] = []
    seen: set[str] = set()
    required = covered = 0
    for position, claim in enumerate(claims):
        claim_id = str(claim.get("claim_id", "")).strip()
        if not claim_id:
            violations.append(f"claim_{position}:claim_id_is_required")
        elif claim_id in seen:
            violations.append(f"claim_{position}:claim_id_must_be_unique")
        seen.add(claim_id)
        citations = claim.get("citation_ids")
        if not isinstance(citations, list) or any(not isinstance(value, str) or not value.strip() for value in citations):
            violations.append(f"claim_{position}:citation_ids_must_be_a_list_of_non_empty_strings")
            citations = []
        if len(citations) != len(set(citations)):
            violations.append(f"claim_{position}:citation_ids_must_be_unique")
        if set(citations) - known_citation_ids:
            violations.append(f"claim_{position}:unknown_citation_reference")
        if claim.get("requires_support") is True:
            required += 1
            covered += bool(citations)
    if required and covered / required < minimum_coverage_ratio:
        violations.append("supported_claim_coverage_below_minimum")
    return tuple(violations)
