from __future__ import annotations


_AUTHORITY_TIERS = {"primary", "official", "secondary", "community"}
_HIGH_AUTHORITY_TIERS = {"primary", "official"}


def citation_source_authority_violations(citations: list[dict[str, object]], *, critical_claim_ids: list[str]) -> tuple[str, ...]:
    violations: list[str] = []
    critical = [claim.strip() for claim in critical_claim_ids if isinstance(claim, str) and claim.strip()]
    if not critical:
        violations.append("at_least_one_critical_claim_is_required")
    if len(set(critical)) != len(critical):
        violations.append("critical_claim_ids_must_be_unique")
    seen_sources: set[str] = set()
    authoritative_claims: set[str] = set()
    for index, citation in enumerate(citations if isinstance(citations, list) else []):
        if not isinstance(citation, dict):
            violations.append(f"citation_{index}:must_be_an_object")
            continue
        source_id = citation.get("source_id")
        if not isinstance(source_id, str) or not source_id.strip():
            violations.append(f"citation_{index}:source_id_is_required")
        elif source_id in seen_sources:
            violations.append(f"citation_{index}:source_id_must_be_unique")
        else:
            seen_sources.add(source_id)
        authority = citation.get("authority_tier")
        if authority not in _AUTHORITY_TIERS:
            violations.append(f"citation_{index}:authority_tier_is_invalid")
        claim_ids = citation.get("claim_ids")
        if not isinstance(claim_ids, list) or not claim_ids or any(not isinstance(claim, str) or not claim.strip() for claim in claim_ids):
            violations.append(f"citation_{index}:claim_ids_must_be_a_non_empty_string_list")
            continue
        if len(set(claim_ids)) != len(claim_ids):
            violations.append(f"citation_{index}:claim_ids_must_be_unique")
        if authority in _HIGH_AUTHORITY_TIERS and citation.get("authority_reviewed") is True:
            authoritative_claims.update(claim_ids)
    for claim_id in sorted(set(critical) - authoritative_claims):
        violations.append(f"critical_claim_{claim_id}:verified_authoritative_source_is_required")
    return tuple(violations)


def critical_claims_have_authoritative_sources(citations: list[dict[str, object]], *, critical_claim_ids: list[str]) -> bool:
    return not citation_source_authority_violations(citations, critical_claim_ids=critical_claim_ids)
