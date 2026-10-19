from __future__ import annotations

from datetime import datetime


def _time(value: object) -> datetime | None:
    if not isinstance(value, str): return None
    try: value = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError: return None
    return value if value.tzinfo is not None and value.utcoffset() is not None else None


def retrieval_source_ownership_violations(sources: object, *, now: datetime, maximum_review_age_seconds: int = 7_776_000) -> tuple[str, ...]:
    if now.tzinfo is None or now.utcoffset() is None or not isinstance(maximum_review_age_seconds, int) or isinstance(maximum_review_age_seconds, bool) or maximum_review_age_seconds < 1: raise ValueError('invalid ownership policy')
    if not isinstance(sources, list) or not sources: return ('sources_must_be_a_non_empty_list',)
    violations: list[str] = []
    seen: set[str] = set()
    for position, source in enumerate(sources):
        prefix = f'source_{position}'
        if not isinstance(source, dict): violations.append(f'{prefix}:source_must_be_an_object'); continue
        source_id = source.get('source_id')
        if not isinstance(source_id, str) or not source_id.strip(): violations.append(f'{prefix}:source_id_is_required')
        elif source_id in seen: violations.append(f'{prefix}:source_id_must_be_unique')
        else: seen.add(source_id)
        if not isinstance(source.get('owner'), str) or not source['owner'].strip(): violations.append(f'{prefix}:owner_is_required')
        if source.get('authority') not in {'internal', 'vendor', 'public'}: violations.append(f'{prefix}:authority_is_unsupported')
        reviewed_at = _time(source.get('reviewed_at'))
        if reviewed_at is None or not 0 <= (now - reviewed_at).total_seconds() <= maximum_review_age_seconds: violations.append(f'{prefix}:ownership_review_is_invalid_stale_or_future_dated')
    return tuple(violations)
