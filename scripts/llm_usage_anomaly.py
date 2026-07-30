from __future__ import annotations

from math import isfinite


def _non_negative_number(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and isfinite(float(value)) and float(value) >= 0


def usage_anomaly_violations(observation: dict[str, object], *, maximum_prompt_tokens: int, maximum_completion_tokens: int, maximum_cost_usd: float, baseline_total_tokens: int | None = None, maximum_growth_ratio: float = 2.0) -> tuple[str, ...]:
    if not isinstance(maximum_prompt_tokens, int) or isinstance(maximum_prompt_tokens, bool) or maximum_prompt_tokens < 0:
        raise ValueError("maximum prompt tokens must be a non-negative integer")
    if not isinstance(maximum_completion_tokens, int) or isinstance(maximum_completion_tokens, bool) or maximum_completion_tokens < 0:
        raise ValueError("maximum completion tokens must be a non-negative integer")
    if not _non_negative_number(maximum_cost_usd):
        raise ValueError("maximum cost must be a finite non-negative number")
    if not _non_negative_number(maximum_growth_ratio) or float(maximum_growth_ratio) < 1:
        raise ValueError("maximum growth ratio must be at least one")
    violations: list[str] = []
    prompt = observation.get("prompt_tokens")
    completion = observation.get("completion_tokens")
    cost = observation.get("cost_usd")
    if not isinstance(prompt, int) or isinstance(prompt, bool) or prompt < 0:
        violations.append("prompt_tokens_must_be_a_non_negative_integer")
    elif prompt > maximum_prompt_tokens:
        violations.append("prompt_tokens_exceed_budget")
    if not isinstance(completion, int) or isinstance(completion, bool) or completion < 0:
        violations.append("completion_tokens_must_be_a_non_negative_integer")
    elif completion > maximum_completion_tokens:
        violations.append("completion_tokens_exceed_budget")
    if not _non_negative_number(cost):
        violations.append("cost_usd_must_be_a_finite_non_negative_number")
    elif float(cost) > float(maximum_cost_usd):
        violations.append("cost_usd_exceeds_budget")
    if baseline_total_tokens is not None:
        if not isinstance(baseline_total_tokens, int) or isinstance(baseline_total_tokens, bool) or baseline_total_tokens <= 0:
            raise ValueError("baseline total tokens must be a positive integer")
        if isinstance(prompt, int) and not isinstance(prompt, bool) and prompt >= 0 and isinstance(completion, int) and not isinstance(completion, bool) and completion >= 0 and prompt + completion > baseline_total_tokens * float(maximum_growth_ratio):
            violations.append("total_token_growth_exceeds_ratio")
    return tuple(violations)


def usage_is_within_expected_bounds(observation: dict[str, object], **policy: object) -> bool:
    return not usage_anomaly_violations(observation, **policy)
