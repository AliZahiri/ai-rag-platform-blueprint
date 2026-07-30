from __future__ import annotations


def evaluation_slice_coverage_violations(samples: list[dict[str, object]], *, required_slices: tuple[str, ...], minimum_samples_per_slice: int = 1) -> tuple[str, ...]:
    if not isinstance(minimum_samples_per_slice, int) or isinstance(minimum_samples_per_slice, bool) or minimum_samples_per_slice <= 0:
        raise ValueError("minimum samples per slice must be a positive integer")
    normalized_required = tuple(str(item).strip() for item in required_slices)
    violations: list[str] = []
    if not normalized_required or any(not item for item in normalized_required):
        violations.append("required_evaluation_slices_are_invalid")
    if len(set(normalized_required)) != len(normalized_required):
        violations.append("required_evaluation_slices_must_be_unique")
    required = set(normalized_required)
    counts = {name: 0 for name in normalized_required if name}
    seen_ids: set[str] = set()
    for index, sample in enumerate(samples):
        sample_id = str(sample.get("sample_id", "")).strip()
        slice_name = str(sample.get("slice", "")).strip()
        if not sample_id:
            violations.append(f"sample_{index}:sample_id_is_required")
        elif sample_id in seen_ids:
            violations.append(f"sample_{index}:sample_id_must_be_unique")
        seen_ids.add(sample_id)
        if not slice_name:
            violations.append(f"sample_{index}:slice_is_required")
        elif slice_name not in required:
            violations.append(f"sample_{index}:slice_is_not_declared")
        else:
            counts[slice_name] += 1
    for slice_name in normalized_required:
        if slice_name and counts.get(slice_name, 0) < minimum_samples_per_slice:
            violations.append(f"slice:{slice_name}:samples_below_minimum")
    return tuple(violations)


def evaluation_slice_coverage_is_sufficient(**inputs: object) -> bool:
    return not evaluation_slice_coverage_violations(**inputs)
