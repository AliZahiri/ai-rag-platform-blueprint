from __future__ import annotations

from datetime import datetime


def _time(value: object) -> datetime | None:
    if not isinstance(value, str): return None
    try: value = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError: return None
    return value if value.tzinfo is not None and value.utcoffset() is not None else None


def retrieval_source_supersession_violations(records: object, *, now: datetime) -> tuple[str, ...]:
    if now.tzinfo is None or now.utcoffset() is None: raise ValueError('now must be timezone-aware')
    if not isinstance(records, list) or not records: return ('supersession_records_must_be_a_non_empty_list',)
    violations: list[str] = []; seen: set[str] = set()
    for position, record in enumerate(records):
        prefix=f'record_{position}'
        if not isinstance(record, dict): violations.append(f'{prefix}:record_must_be_an_object'); continue
        source, successor = record.get('source_id'), record.get('successor_source_id')
        if not isinstance(source, str) or not source.strip(): violations.append(f'{prefix}:source_id_is_required')
        elif source in seen: violations.append(f'{prefix}:source_id_must_be_unique')
        else: seen.add(source)
        if not isinstance(successor, str) or not successor.strip() or successor == source: violations.append(f'{prefix}:successor_source_id_must_be_distinct')
        if not isinstance(record.get('approval_reference'), str) or not record['approval_reference'].strip(): violations.append(f'{prefix}:approval_reference_is_required')
        effective_at=_time(record.get('effective_at'))
        if effective_at is None: violations.append(f'{prefix}:effective_at_must_be_timezone_aware')
        elif effective_at <= now and record.get('source_is_active') is True: violations.append(f'{prefix}:superseded_source_must_not_remain_active')
    return tuple(violations)
