from __future__ import annotations


def uncovered_claim_ids(claim_ids: list[str] | tuple[str, ...], evidence_by_claim: dict[str, list[str]]) -> tuple[str, ...]:
    missing: list[str] = []
    for claim_id in claim_ids:
        normalized = claim_id.strip()
        evidence_ids = evidence_by_claim.get(normalized, [])
        if not normalized or not any(evidence_id.strip() for evidence_id in evidence_ids):
            missing.append(normalized or "unknown")
    return tuple(missing)


def evidence_coverage_is_complete(claim_ids: list[str] | tuple[str, ...], evidence_by_claim: dict[str, list[str]]) -> bool:
    return bool(claim_ids) and not uncovered_claim_ids(claim_ids, evidence_by_claim)
