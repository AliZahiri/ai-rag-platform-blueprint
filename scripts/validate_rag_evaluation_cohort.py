from __future__ import annotations

from datetime import datetime

def _time(value: object) -> datetime | None:
    if not isinstance(value, str): return None
    try: parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError: return None
    return parsed if parsed.tzinfo and parsed.utcoffset() is not None else None

def rag_evaluation_violations(evidence: object, *, dataset_id: str, now: datetime, minimum_queries: int = 50, minimum_citation_precision: float = 0.9, maximum_age_seconds: int = 86400) -> tuple[str, ...]:
    if not isinstance(dataset_id, str) or not dataset_id.strip() or now.tzinfo is None or minimum_queries < 1 or not 0 < minimum_citation_precision <= 1 or maximum_age_seconds < 1: raise ValueError('invalid policy')
    if not isinstance(evidence, dict): return ('evaluation_evidence_must_be_an_object',)
    violations: list[str] = []
    if evidence.get('dataset_id') != dataset_id: violations.append('evaluation_dataset_must_match_approved_cohort')
    if evidence.get('completed') is not True: violations.append('evaluation_must_complete')
    queries = evidence.get('query_count')
    if type(queries) is not int or queries < minimum_queries: violations.append('evaluation_query_count_is_below_minimum')
    precision = evidence.get('citation_precision')
    if type(precision) not in (int, float) or isinstance(precision, bool) or not minimum_citation_precision <= float(precision) <= 1: violations.append('citation_precision_is_below_minimum')
    observed = _time(evidence.get('observed_at'))
    if observed is None or not 0 <= (now - observed).total_seconds() <= maximum_age_seconds: violations.append('evaluation_evidence_is_invalid_stale_or_future_dated')
    return tuple(violations)
