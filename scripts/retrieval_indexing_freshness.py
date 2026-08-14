from __future__ import annotations

from datetime import datetime
import re


_SHA256 = re.compile(r"[0-9a-f]{64}\Z")


def _timestamp(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None and parsed.utcoffset() is not None else None


def retrieval_indexing_freshness_violations(records: list[dict[str, object]], *, now: datetime, maximum_delay_hours: int = 24) -> tuple[str, ...]:
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("current time must be timezone-aware")
    if not isinstance(maximum_delay_hours, int) or isinstance(maximum_delay_hours, bool) or maximum_delay_hours <= 0:
        raise ValueError("maximum delay hours must be positive")
    if not records:
        return ("at_least_one_indexing_record_is_required",)
    violations: list[str] = []
    seen_ids: set[str] = set()
    for index, record in enumerate(records):
        source_id = record.get("source_id")
        if not isinstance(source_id, str) or not source_id.strip():
            violations.append(f"record_{index}:source_id_is_required")
        elif source_id in seen_ids:
            violations.append(f"record_{index}:source_id_must_be_unique")
        if isinstance(source_id, str):
            seen_ids.add(source_id)
        if not isinstance(record.get("content_sha256"), str) or not _SHA256.fullmatch(record["content_sha256"]):
            violations.append(f"record_{index}:content_sha256_is_invalid")
        source_updated_at = _timestamp(record.get("source_updated_at"))
        indexed_at = _timestamp(record.get("indexed_at"))
        if source_updated_at is None or indexed_at is None:
            violations.append(f"record_{index}:timestamps_must_be_timezone_aware")
            continue
        delay = (indexed_at - source_updated_at).total_seconds()
        age = (now - indexed_at).total_seconds()
        if delay < 0 or delay > maximum_delay_hours * 3600:
            violations.append(f"record_{index}:indexing_delay_exceeds_budget")
        if age < 0 or age > maximum_delay_hours * 3600:
            violations.append(f"record_{index}:index_observation_is_not_fresh")
    return tuple(violations)


def retrieval_indexing_is_fresh(records: list[dict[str, object]], **policy: object) -> bool:
    return not retrieval_indexing_freshness_violations(records, **policy)
