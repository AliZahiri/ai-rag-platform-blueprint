from __future__ import annotations


def citation_source_warnings(sources: list[dict[str, object]]) -> tuple[str, ...]:
    warnings: list[str] = []
    identifiers = [
        value.strip() if isinstance(value := source.get("source_id"), str) else ""
        for source in sources
    ]
    if any(not identifier for identifier in identifiers):
        warnings.append("citation_source_id_is_required")
    if len(set(identifiers)) != len(identifiers):
        warnings.append("citation_source_ids_must_be_unique")
    if any(not isinstance(location := source.get("location"), str) or not location.strip() for source in sources):
        warnings.append("citation_source_location_is_required")
    return tuple(warnings)


def citations_are_traceable(sources: list[dict[str, object]]) -> bool:
    return bool(sources) and not citation_source_warnings(sources)
