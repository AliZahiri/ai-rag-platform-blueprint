from __future__ import annotations

from scripts.context_window_budget import context_budget_warnings
from scripts.provider_capability_match import provider_capability_violations


def provider_route_preflight(provider: dict[str, object], *, required_capabilities: tuple[str, ...], required_context_tokens: int, prompt_tokens: int, completion_tokens: int, max_total_tokens: int) -> dict[str, object]:
    violations = list(provider_capability_violations(provider, required=required_capabilities, required_context_tokens=required_context_tokens))
    violations.extend(context_budget_warnings([prompt_tokens], max_context_tokens=max_total_tokens, reserved_output_tokens=completion_tokens))
    return {"eligible": not violations, "violations": tuple(violations), "estimated_total_tokens": prompt_tokens + completion_tokens}
