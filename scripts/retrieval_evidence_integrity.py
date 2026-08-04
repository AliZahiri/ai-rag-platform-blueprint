from __future__ import annotations

import re


_SHA256 = re.compile(r"[0-9a-f]{64}\Z")


def retrieval_evidence_integrity_violations(records: list[dict[str, object]], *, expected_hashes: dict[str, str]) -> tuple[str, ...]:
    if not expected_hashes or any(not str(source).strip() or not isinstance(digest, str) or not _SHA256.fullmatch(digest) for source, digest in expected_hashes.items()):
        raise ValueError("expected hashes must map non-empty source ids to lowercase SHA-256 digests")
    if not records:
        return ("at_least_one_retrieval_record_is_required",)
    violations: list[str] = []
    seen: set[str] = set()
    for position, record in enumerate(records):
        source_id = str(record.get("source_id", "")).strip()
        digest = record.get("content_sha256")
        if not source_id:
            violations.append(f"record_{position}:source_id_is_required")
        elif source_id in seen:
            violations.append(f"record_{position}:source_id_must_be_unique")
        seen.add(source_id)
        if source_id and source_id not in expected_hashes:
            violations.append(f"record_{position}:source_is_missing_from_manifest")
        if not isinstance(digest, str) or not _SHA256.fullmatch(digest):
            violations.append(f"record_{position}:content_sha256_is_invalid")
        elif source_id in expected_hashes and digest != expected_hashes[source_id]:
            violations.append(f"record_{position}:content_sha256_mismatch")
    return tuple(violations)


def retrieval_evidence_has_integrity(records: list[dict[str, object]], **policy: object) -> bool:
    return not retrieval_evidence_integrity_violations(records, **policy)
