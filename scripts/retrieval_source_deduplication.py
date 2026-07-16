from __future__ import annotations


def unique_source_ids(results: list[dict[str, object]]) -> tuple[str, ...]:
    identifiers: list[str] = []
    for result in results:
        source_id = str(result.get("source_id", "")).strip()
        if source_id and source_id not in identifiers:
            identifiers.append(source_id)
    return tuple(identifiers)


def duplicate_source_ids(results: list[dict[str, object]]) -> tuple[str, ...]:
    seen: set[str] = set()
    duplicates: list[str] = []
    for result in results:
        source_id = str(result.get("source_id", "")).strip()
        if source_id and source_id in seen and source_id not in duplicates:
            duplicates.append(source_id)
        seen.add(source_id)
    return tuple(duplicates)
