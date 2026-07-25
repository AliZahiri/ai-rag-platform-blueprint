from __future__ import annotations

from math import isfinite


_METRICS = ("groundedness", "citation_precision", "answer_relevance")


def _valid_score(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and isfinite(float(value)) and 0 <= float(value) <= 1


def evaluation_regression_violations(*, baseline: dict[str, object], candidate: dict[str, object], maximum_regression: float) -> tuple[str, ...]:
    if not _valid_score(maximum_regression):
        raise ValueError("maximum regression must be between zero and one")
    violations: list[str] = []
    for metric in _METRICS:
        baseline_score = baseline.get(metric)
        candidate_score = candidate.get(metric)
        if not _valid_score(baseline_score):
            violations.append(f"baseline:{metric}:score_must_be_between_zero_and_one")
            continue
        if not _valid_score(candidate_score):
            violations.append(f"candidate:{metric}:score_must_be_between_zero_and_one")
            continue
        if float(baseline_score) - float(candidate_score) > maximum_regression:
            violations.append(f"{metric}:regression_exceeds_budget")
    return tuple(violations)


def evaluation_regression_is_acceptable(**inputs: object) -> bool:
    return not evaluation_regression_violations(**inputs)
