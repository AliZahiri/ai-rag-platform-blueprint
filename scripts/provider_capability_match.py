from __future__ import annotations


def provider_capability_violations(provider: dict[str, object], *, required: tuple[str, ...], required_context_tokens: int) -> tuple[str, ...]:
    violations: list[str] = []
    if required_context_tokens <= 0:
        raise ValueError("required context tokens must be positive")
    capabilities = provider.get("capabilities")
    if not isinstance(capabilities, dict):
        violations.append("capabilities_must_be_object")
    else:
        for capability in required:
            if capabilities.get(capability) is not True:
                violations.append(f"capability_{capability}_is_required")
    max_context_tokens = provider.get("max_context_tokens")
    if not isinstance(max_context_tokens, int) or isinstance(max_context_tokens, bool) or max_context_tokens < required_context_tokens:
        violations.append("context_window_is_insufficient")
    return tuple(violations)


def provider_matches_workload(provider: dict[str, object], *, required: tuple[str, ...], required_context_tokens: int) -> bool:
    return not provider_capability_violations(provider, required=required, required_context_tokens=required_context_tokens)
