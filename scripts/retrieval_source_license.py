from __future__ import annotations


_ALLOWED_LICENSES = {"CC-BY-4.0", "CC0-1.0", "MIT", "Apache-2.0", "Proprietary-Internal"}


def retrieval_source_license_violations(sources: list[dict[str, object]]) -> tuple[str, ...]:
    if not sources:
        return ("at_least_one_source_is_required",)
    violations: list[str] = []
    seen_ids: set[str] = set()
    for index, source in enumerate(sources):
        source_id = source.get("source_id")
        if not isinstance(source_id, str) or not source_id.strip():
            violations.append(f"source_{index}:source_id_is_required")
        elif source_id in seen_ids:
            violations.append(f"source_{index}:source_id_must_be_unique")
        seen_ids.add(source_id)
        if source.get("license") not in _ALLOWED_LICENSES:
            violations.append(f"source_{index}:license_is_not_allowed")
        if source.get("ingestion_permitted") is not True:
            violations.append(f"source_{index}:ingestion_permission_is_required")
        if not isinstance(source.get("owner"), str) or not source["owner"].strip():
            violations.append(f"source_{index}:owner_is_required")
    return tuple(violations)


def retrieval_source_license_is_safe(sources: list[dict[str, object]]) -> bool:
    return not retrieval_source_license_violations(sources)
