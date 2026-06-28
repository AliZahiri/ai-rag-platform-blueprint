from __future__ import annotations


def fallback_budget_warnings(policy: dict[str, object]) -> tuple[str, ...]:
    warnings: list[str] = []
    if not policy.get("fallback_alias"):
        warnings.append("fallback_alias_missing")
    estimated_cost = policy.get("estimated_cost_usd")
    request_budget = policy.get("request_budget_usd")
    retry_count = policy.get("retry_count", 0)
    if not isinstance(estimated_cost, (int, float)) or estimated_cost < 0:
        warnings.append("estimated_cost_usd_must_be_non_negative")
    if not isinstance(request_budget, (int, float)) or request_budget <= 0:
        warnings.append("request_budget_usd_must_be_positive")
    if isinstance(estimated_cost, (int, float)) and isinstance(request_budget, (int, float)) and estimated_cost > request_budget:
        warnings.append("fallback_cost_exceeds_request_budget")
    if not isinstance(retry_count, int) or retry_count < 0:
        warnings.append("retry_count_must_be_non_negative")
    if isinstance(retry_count, int) and retry_count > 2:
        warnings.append("retry_count_exceeds_fallback_policy")
    if policy.get("required_capabilities_preserved") is not True:
        warnings.append("required_capabilities_must_be_preserved")
    return tuple(warnings)


def fallback_budget_is_safe(policy: dict[str, object]) -> bool:
    return not fallback_budget_warnings(policy)
