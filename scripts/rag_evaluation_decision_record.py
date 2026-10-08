from __future__ import annotations


def decision_record_violations(record: object, *, minimum_reviewer_count: int = 2) -> tuple[str, ...]:
    if not isinstance(minimum_reviewer_count, int) or isinstance(minimum_reviewer_count, bool) or minimum_reviewer_count < 1:
        raise ValueError("minimum_reviewer_count must be a positive integer")
    if not isinstance(record, dict):
        return ("decision_record_must_be_an_object",)
    violations: list[str] = []
    for field in ("release_id", "baseline_id", "candidate_id"):
        if not isinstance(record.get(field), str) or not record[field].strip():
            violations.append(f"{field}_is_required")
    if record.get("baseline_id") == record.get("candidate_id"):
        violations.append("baseline_and_candidate_must_differ")
    if record.get("decision") not in {"approve", "reject"}:
        violations.append("decision_must_be_approve_or_reject")
    reviewers = record.get("reviewer_ids")
    if not isinstance(reviewers, list) or len(reviewers) < minimum_reviewer_count:
        violations.append("minimum_reviewer_count_not_met")
    elif any(not isinstance(value, str) or not value.strip() for value in reviewers) or len(set(reviewers)) != len(reviewers):
        violations.append("reviewer_ids_must_be_unique_non_empty_strings")
    metrics = record.get("metrics")
    if not isinstance(metrics, list) or not metrics:
        violations.append("at_least_one_metric_is_required")
    else:
        for index, metric in enumerate(metrics):
            if not isinstance(metric, dict):
                violations.append(f"metric_{index}_must_be_an_object")
                continue
            delta, budget = metric.get("delta"), metric.get("maximum_regression")
            if not isinstance(delta, (int, float)) or isinstance(delta, bool) or not isinstance(budget, (int, float)) or isinstance(budget, bool) or budget < 0:
                violations.append(f"metric_{index}_must_have_numeric_delta_and_non_negative_budget")
            elif delta < -budget:
                violations.append(f"metric_{index}_exceeds_regression_budget")
    return tuple(violations)


def decision_record_is_ready(record: object, **policy: object) -> bool:
    return not decision_record_violations(record, **policy)
