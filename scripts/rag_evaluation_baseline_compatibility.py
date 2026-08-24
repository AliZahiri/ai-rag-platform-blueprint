from __future__ import annotations

import re


_SHA256 = re.compile(r"[0-9a-f]{64}\Z")


def baseline_compatibility_violations(candidate: dict[str, object], baseline: dict[str, object], *, minimum_samples: int = 30) -> tuple[str, ...]:
    if not isinstance(minimum_samples, int) or isinstance(minimum_samples, bool) or minimum_samples < 1:
        raise ValueError("minimum_samples must be positive")
    violations: list[str] = []
    for field in ("dataset_sha256", "scorer_version"):
        left, right = candidate.get(field), baseline.get(field)
        if field == "dataset_sha256" and (not isinstance(left, str) or not _SHA256.fullmatch(left)):
            violations.append("candidate_dataset_sha256_is_invalid")
        if left != right:
            violations.append(f"{field}_must_match_baseline")
    for label, snapshot in (("candidate", candidate), ("baseline", baseline)):
        samples = snapshot.get("sample_count")
        if not isinstance(samples, int) or isinstance(samples, bool) or samples < minimum_samples:
            violations.append(f"{label}_sample_count_is_below_minimum")
    candidate_metrics, baseline_metrics = candidate.get("metrics"), baseline.get("metrics")
    if not isinstance(candidate_metrics, list) or not candidate_metrics or any(not isinstance(item, str) or not item.strip() for item in candidate_metrics):
        violations.append("candidate_metrics_must_be_a_non_empty_string_list")
    elif set(candidate_metrics) != set(baseline_metrics) if isinstance(baseline_metrics, list) else True:
        violations.append("metric_set_must_match_baseline")
    return tuple(violations)


def evaluation_baseline_is_compatible(candidate: dict[str, object], baseline: dict[str, object], **policy: object) -> bool:
    return not baseline_compatibility_violations(candidate, baseline, **policy)
