from __future__ import annotations

import re
from datetime import datetime


_SHA256 = re.compile(r"[0-9a-f]{64}\Z")


def _timestamp(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None and parsed.utcoffset() is not None else None


def citation_provenance_violations(citations: list[dict[str, object]], *, index_snapshot: str) -> tuple[str, ...]:
    if not isinstance(index_snapshot, str) or not index_snapshot.strip():
        raise ValueError("index snapshot must be a non-empty string")
    if not citations:
        return ("at_least_one_citation_is_required",)

    violations: list[str] = []
    seen_source_ids: set[str] = set()
    for index, citation in enumerate(citations):
        source_id = citation.get("source_id")
        if not isinstance(source_id, str) or not source_id.strip():
            violations.append(f"citation_{index}:source_id_is_required")
        elif source_id in seen_source_ids:
            violations.append(f"citation_{index}:source_id_must_be_unique")
        seen_source_ids.add(source_id)
        digest = citation.get("content_sha256")
        if not isinstance(digest, str) or not _SHA256.fullmatch(digest):
            violations.append(f"citation_{index}:content_sha256_is_invalid")
        if _timestamp(citation.get("captured_at")) is None:
            violations.append(f"citation_{index}:captured_at_must_be_timezone_aware")
        if citation.get("index_snapshot") != index_snapshot:
            violations.append(f"citation_{index}:index_snapshot_must_match_answer")
    return tuple(violations)


def citation_provenance_is_complete(citations: list[dict[str, object]], *, index_snapshot: str) -> bool:
    return not citation_provenance_violations(citations, index_snapshot=index_snapshot)
