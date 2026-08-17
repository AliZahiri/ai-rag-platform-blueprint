from __future__ import annotations


def source_license_violations(sources: list[dict[str, object]], allowed_licenses: set[str]) -> tuple[str, ...]:
    violations: list[str] = []
    normalized_allowed = {license_id.strip().lower() for license_id in allowed_licenses if isinstance(license_id, str) and license_id.strip()}
    if not normalized_allowed:
        return ("allowed_licenses_must_not_be_empty",)
    seen_ids: set[str] = set()
    for index, source in enumerate(sources):
        source_id = source.get("source_id")
        license_id = source.get("license")
        if not isinstance(source_id, str) or not source_id.strip():
            violations.append(f"source_{index}:source_id_is_required")
        elif source_id in seen_ids:
            violations.append(f"source_{index}:source_id_must_be_unique")
        else:
            seen_ids.add(source_id)
        if not isinstance(license_id, str) or license_id.strip().lower() not in normalized_allowed:
            violations.append(f"source_{index}:license_is_not_allowed")
    return tuple(violations)


def sources_have_allowed_licenses(sources: list[dict[str, object]], allowed_licenses: set[str]) -> bool:
    return not source_license_violations(sources, allowed_licenses)
