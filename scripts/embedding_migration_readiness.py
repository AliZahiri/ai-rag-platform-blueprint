from __future__ import annotations

from math import isfinite


def embedding_migration_violations(evidence: dict[str, object], *, minimum_sample_count: int = 20, minimum_overlap_ratio: float = 0.8) -> tuple[str, ...]:
    if not isinstance(minimum_sample_count, int) or isinstance(minimum_sample_count, bool) or minimum_sample_count <= 0:
        raise ValueError("minimum sample count must be a positive integer")
    if not isinstance(minimum_overlap_ratio, (int, float)) or isinstance(minimum_overlap_ratio, bool) or not isfinite(float(minimum_overlap_ratio)) or not 0 <= minimum_overlap_ratio <= 1:
        raise ValueError("minimum overlap ratio must be finite and between zero and one")
    violations: list[str] = []
    for field in ("source_dimension", "target_dimension"):
        value = evidence.get(field)
        if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
            violations.append(f"{field}_must_be_a_positive_integer")
    sample_count = evidence.get("sample_count")
    if not isinstance(sample_count, int) or isinstance(sample_count, bool) or sample_count < minimum_sample_count:
        violations.append("sample_count_below_minimum")
    overlap = evidence.get("top_result_overlap_ratio")
    if not isinstance(overlap, (int, float)) or isinstance(overlap, bool) or not isfinite(float(overlap)) or not 0 <= float(overlap) <= 1:
        violations.append("top_result_overlap_ratio_must_be_between_zero_and_one")
    elif float(overlap) < minimum_overlap_ratio:
        violations.append("top_result_overlap_ratio_below_minimum")
    for field in ("dual_write_enabled", "backfill_complete", "source_query_passed", "target_query_passed"):
        if evidence.get(field) is not True:
            violations.append(f"{field}_must_be_true")
    return tuple(violations)


def embedding_migration_is_ready(evidence: dict[str, object], **policy: object) -> bool:
    return not embedding_migration_violations(evidence, **policy)
