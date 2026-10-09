from __future__ import annotations

import math
import re


_METRIC_ID = re.compile(r"[a-z][a-z0-9_]*\Z")
_DIRECTIONS = {"higher_is_better", "lower_is_better"}


def evaluation_metric_contract_violations(metrics: object) -> tuple[str, ...]:
    """Return deterministic validation errors for release-comparison metrics.

    The numeric values intentionally have no fixed range: this contract supports
    normalized quality scores as well as measurements such as latency or cost.
    """
    if not isinstance(metrics, list) or not metrics:
        return ("at_least_one_metric_is_required",)

    violations: list[str] = []
    identifiers: set[str] = set()
    for index, metric in enumerate(metrics):
        prefix = f"metric_{index}"
        if not isinstance(metric, dict):
            violations.append(f"{prefix}:must_be_an_object")
            continue

        identifier = metric.get("metric_id")
        if not isinstance(identifier, str) or not _METRIC_ID.fullmatch(identifier):
            violations.append(f"{prefix}:metric_id_must_be_a_stable_identifier")
        elif identifier in identifiers:
            violations.append(f"{prefix}:metric_id_must_be_unique")
        else:
            identifiers.add(identifier)

        direction = metric.get("direction")
        if direction not in _DIRECTIONS:
            violations.append(f"{prefix}:direction_is_invalid")

        baseline = metric.get("baseline")
        candidate = metric.get("candidate")
        maximum_regression = metric.get("maximum_regression")
        values = {
            "baseline": baseline,
            "candidate": candidate,
            "maximum_regression": maximum_regression,
        }
        for field, value in values.items():
            if not _is_finite_number(value):
                violations.append(f"{prefix}:{field}_must_be_a_finite_number")
        if _is_finite_number(maximum_regression) and maximum_regression < 0:
            violations.append(f"{prefix}:maximum_regression_must_be_non_negative")

        if (
            direction in _DIRECTIONS
            and all(_is_finite_number(value) for value in values.values())
            and maximum_regression >= 0
            and _regression_exceeds_budget(
                baseline=baseline,
                candidate=candidate,
                maximum_regression=maximum_regression,
                direction=direction,
            )
        ):
            violations.append(f"{prefix}:regression_exceeds_maximum")
    return tuple(violations)


def evaluation_metric_contract_is_valid(metrics: object) -> bool:
    return not evaluation_metric_contract_violations(metrics)


def _is_finite_number(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _regression_exceeds_budget(
    *, baseline: float | int, candidate: float | int, maximum_regression: float | int, direction: str
) -> bool:
    if direction == "higher_is_better":
        regression = baseline - candidate
    else:
        regression = candidate - baseline
    return regression > maximum_regression and not math.isclose(
        regression, maximum_regression, rel_tol=1e-12, abs_tol=1e-12
    )
