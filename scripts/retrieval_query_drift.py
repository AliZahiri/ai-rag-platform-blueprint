from __future__ import annotations

from math import isclose, isfinite


def query_distribution_drift_violations(baseline: dict[str, object], candidate: dict[str, object], *, minimum_samples: int = 100, maximum_total_variation: float = 0.20) -> tuple[str, ...]:
    if not isinstance(minimum_samples, int) or isinstance(minimum_samples, bool) or minimum_samples < 1:
        raise ValueError("minimum_samples must be a positive integer")
    if not _probability(maximum_total_variation):
        raise ValueError("maximum_total_variation must be a probability")
    violations: list[str] = []
    distributions: dict[str, dict[str, float]] = {}
    for label, snapshot in (("baseline", baseline), ("candidate", candidate)):
        if not isinstance(snapshot.get("snapshot_id"), str) or not snapshot["snapshot_id"].strip():
            violations.append(f"{label}:snapshot_id_is_required")
        samples = snapshot.get("sample_count")
        if not isinstance(samples, int) or isinstance(samples, bool) or samples < minimum_samples:
            violations.append(f"{label}:sample_count_is_below_minimum")
        distribution = snapshot.get("distribution")
        if not isinstance(distribution, dict) or not distribution:
            violations.append(f"{label}:distribution_must_be_a_non_empty_object")
            continue
        normalized: dict[str, float] = {}
        for category, share in distribution.items():
            if not isinstance(category, str) or not category.strip() or not _probability(share):
                violations.append(f"{label}:distribution_entries_must_be_named_probabilities")
                break
            normalized[category] = float(share)
        else:
            if not isclose(sum(normalized.values()), 1.0, rel_tol=0.0, abs_tol=1e-6):
                violations.append(f"{label}:distribution_must_sum_to_one")
            else:
                distributions[label] = normalized
    if len(distributions) == 2:
        categories = set(distributions["baseline"]) | set(distributions["candidate"])
        distance = 0.5 * sum(abs(distributions["baseline"].get(category, 0.0) - distributions["candidate"].get(category, 0.0)) for category in categories)
        if distance > maximum_total_variation:
            violations.append("query_distribution_total_variation_exceeds_budget")
    return tuple(violations)


def query_distribution_is_stable(baseline: dict[str, object], candidate: dict[str, object], **policy: object) -> bool:
    return not query_distribution_drift_violations(baseline, candidate, **policy)


def _probability(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and isfinite(float(value)) and 0 <= value <= 1
