from __future__ import annotations

from datetime import datetime


def _time(value: object) -> datetime | None:
    if not isinstance(value, str): return None
    try: value = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError: return None
    return value if value.tzinfo is not None and value.utcoffset() is not None else None


def retrieval_source_deprecation_violations(records: object, *, now: datetime) -> tuple[str, ...]:
    if now.tzinfo is None or now.utcoffset() is None: raise ValueError('now must be timezone-aware')
    if not isinstance(records, list) or not records: return ('deprecation_records_must_be_a_non_empty_list',)
    violations: list[str] = []; seen: set[str] = set()
    for position, record in enumerate(records):
        prefix = f'record_{position}'
        if not isinstance(record, dict): violations.append(f'{prefix}:record_must_be_an_object'); continue
        source_id = record.get('source_id')
        if not isinstance(source_id, str) or not source_id.strip(): violations.append(f'{prefix}:source_id_is_required')
        elif source_id in seen: violations.append(f'{prefix}:source_id_must_be_unique')
        else: seen.add(source_id)
        effective_at = _time(record.get('effective_at'))
        if effective_at is None or effective_at > now: violations.append(f'{prefix}:effective_at_must_not_be_future_dated')
        if record.get('disposition') not in {'remove', 'replace'}: violations.append(f'{prefix}:disposition_must_be_remove_or_replace')
        if record.get('disposition') == 'replace' and (not isinstance(record.get('replacement_source_id'), str) or not record['replacement_source_id'].strip()): violations.append(f'{prefix}:replacement_source_id_is_required')
    return tuple(violations)
