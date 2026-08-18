from __future__ import annotations


def model_latency_budget_violations(observations: list[dict[str, object]], *, max_latency_seconds: float = 30.0) -> tuple[str, ...]:
    if not isinstance(max_latency_seconds, (int, float)) or isinstance(max_latency_seconds, bool) or max_latency_seconds <= 0:
        raise ValueError("maximum latency must be positive")
    if not observations:
        return ("at_least_one_latency_observation_is_required",)
    violations: list[str] = []
    for index, observation in enumerate(observations):
        if not isinstance(observation.get("request_id"), str) or not observation["request_id"].strip():
            violations.append(f"observation_{index}:request_id_is_required")
        latency = observation.get("latency_seconds")
        if not isinstance(latency, (int, float)) or isinstance(latency, bool) or latency < 0:
            violations.append(f"observation_{index}:latency_seconds_must_be_non_negative")
        elif latency > max_latency_seconds:
            violations.append(f"observation_{index}:latency_exceeds_budget")
    return tuple(violations)


def model_latency_is_within_budget(observations: list[dict[str, object]], **policy: object) -> bool:
    return not model_latency_budget_violations(observations, **policy)
