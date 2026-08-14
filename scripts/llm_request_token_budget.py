from __future__ import annotations


def llm_request_token_budget_violations(request: dict[str, object], route: dict[str, object]) -> tuple[str, ...]:
    violations: list[str] = []
    for field, source in (("input_tokens", request), ("reserved_output_tokens", request), ("context_window_tokens", route), ("max_request_tokens", route)):
        value = source.get(field)
        if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
            violations.append(f"{field}_must_be_positive")
    if violations:
        return tuple(violations)
    requested = request["input_tokens"] + request["reserved_output_tokens"]
    if requested > route["context_window_tokens"]:
        violations.append("request_exceeds_context_window")
    if requested > route["max_request_tokens"]:
        violations.append("request_exceeds_route_budget")
    return tuple(violations)


def llm_request_is_within_token_budget(request: dict[str, object], route: dict[str, object]) -> bool:
    return not llm_request_token_budget_violations(request, route)
