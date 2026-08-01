from __future__ import annotations


def retrieval_lineage_violations(records: list[dict[str, object]], *, expected_corpus_snapshot: str, expected_index_version: str) -> tuple[str, ...]:
    expected_snapshot = str(expected_corpus_snapshot).strip()
    expected_index = str(expected_index_version).strip()
    if not expected_snapshot or not expected_index:
        raise ValueError("expected corpus snapshot and index version are required")
    if not records:
        return ("at_least_one_retrieval_record_is_required",)
    violations: list[str] = []
    seen_sources: set[str] = set()
    for position, record in enumerate(records):
        source_id = str(record.get("source_id", "")).strip()
        if not source_id:
            violations.append(f"record_{position}:source_id_is_required")
        elif source_id in seen_sources:
            violations.append(f"record_{position}:source_id_must_be_unique")
        seen_sources.add(source_id)
        if str(record.get("corpus_snapshot", "")).strip() != expected_snapshot:
            violations.append(f"record_{position}:corpus_snapshot_mismatch")
        if str(record.get("index_version", "")).strip() != expected_index:
            violations.append(f"record_{position}:index_version_mismatch")
    return tuple(violations)


def retrieval_lineage_is_consistent(records: list[dict[str, object]], **policy: object) -> bool:
    return not retrieval_lineage_violations(records, **policy)
