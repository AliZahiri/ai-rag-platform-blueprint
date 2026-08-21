from __future__ import annotations

from datetime import datetime


def retrieval_cache_violations(entry: dict[str, object], *, max_ttl_seconds: int = 3600) -> tuple[str, ...]:
    if not isinstance(max_ttl_seconds, int) or isinstance(max_ttl_seconds, bool) or max_ttl_seconds < 1:
        return ("max_ttl_seconds_must_be_positive",)
    violations: list[str] = []
    for field in ("cache_key", "citation_scope"):
        if not isinstance(entry.get(field), str) or not entry[field].strip():
            violations.append(f"{field}_is_required")
    ttl = entry.get("ttl_seconds")
    if not isinstance(ttl, int) or isinstance(ttl, bool) or not 1 <= ttl <= max_ttl_seconds:
        violations.append("ttl_seconds_must_be_within_policy")
    if _parse_timestamp(entry.get("cached_at")) is None:
        violations.append("cached_at_must_be_timezone_aware")
    if entry.get("contains_sensitive_data") is True:
        violations.append("sensitive_entries_must_not_be_cached")
    return tuple(violations)


def retrieval_cache_entry_is_safe(entry: dict[str, object], *, max_ttl_seconds: int = 3600) -> bool:
    return not retrieval_cache_violations(entry, max_ttl_seconds=max_ttl_seconds)


def _parse_timestamp(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None and parsed.utcoffset() is not None else None
