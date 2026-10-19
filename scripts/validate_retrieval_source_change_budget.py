from __future__ import annotations

import re


_DIGEST = re.compile(r"sha256:[0-9a-f]{64}\Z")
_SOURCE_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:/-]*\Z")


def _manifest_index(manifest: object, label: str) -> tuple[dict[str, str], list[str]]:
    if not isinstance(manifest, list) or not manifest:
        return {}, [f"{label}_manifest_must_be_a_non_empty_list"]
    index: dict[str, str] = {}
    violations: list[str] = []
    for position, item in enumerate(manifest):
        if not isinstance(item, dict):
            violations.append(f"{label}_{position}:source_must_be_an_object")
            continue
        source_id = item.get("source_id")
        digest = item.get("content_sha256")
        if not isinstance(source_id, str) or not _SOURCE_ID.fullmatch(source_id):
            violations.append(f"{label}_{position}:source_id_is_invalid")
            continue
        if source_id in index:
            violations.append(f"{label}_{position}:source_id_must_be_unique")
            continue
        if not isinstance(digest, str) or not _DIGEST.fullmatch(digest):
            violations.append(f"{label}_{position}:content_sha256_is_invalid")
            continue
        index[source_id] = digest
    return index, violations


def retrieval_source_change_budget_violations(
    baseline: object,
    candidate: object,
    *,
    maximum_changed_fraction: float = 0.20,
    approval_reference: object = None,
) -> tuple[str, ...]:
    if (
        not isinstance(maximum_changed_fraction, (int, float))
        or isinstance(maximum_changed_fraction, bool)
        or not 0 <= maximum_changed_fraction <= 1
    ):
        raise ValueError("maximum_changed_fraction must be between zero and one")
    baseline_index, violations = _manifest_index(baseline, "baseline")
    candidate_index, candidate_violations = _manifest_index(candidate, "candidate")
    violations.extend(candidate_violations)
    if violations:
        return tuple(violations)

    all_source_ids = set(baseline_index) | set(candidate_index)
    changed_count = sum(
        baseline_index.get(source_id) != candidate_index.get(source_id)
        for source_id in all_source_ids
    )
    changed_fraction = changed_count / len(baseline_index)
    has_approval = isinstance(approval_reference, str) and bool(approval_reference.strip())
    if changed_fraction > maximum_changed_fraction and not has_approval:
        violations.append("source_change_budget_exceeded_without_approval")
    return tuple(violations)


def retrieval_source_change_is_within_budget(
    baseline: object, candidate: object, **policy: object
) -> bool:
    return not retrieval_source_change_budget_violations(baseline, candidate, **policy)
