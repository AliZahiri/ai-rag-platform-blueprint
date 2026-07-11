from __future__ import annotations

REQUIRED_SNAPSHOT_FIELDS = ("question_id", "retrieved_sources", "has_citation", "freshness_ok", "review_passed")


def snapshot_warnings(snapshot: dict[str, object], *, min_sources: int = 2) -> tuple[str, ...]:
    warnings: list[str] = []
    for field in REQUIRED_SNAPSHOT_FIELDS:
        if field not in snapshot:
            warnings.append(f"{field}_is_required")

    sources = snapshot.get("retrieved_sources")
    if not isinstance(sources, int) or sources < min_sources:
        warnings.append("retrieved_sources_below_threshold")
    if snapshot.get("has_citation") is not True:
        warnings.append("answer_missing_citation")
    if snapshot.get("freshness_ok") is not True:
        warnings.append("source_freshness_not_verified")
    if snapshot.get("review_passed") is not True:
        warnings.append("review_not_passed")
    return tuple(warnings)


def snapshot_passes(snapshot: dict[str, object], *, min_sources: int = 2) -> bool:
    return not snapshot_warnings(snapshot, min_sources=min_sources)
