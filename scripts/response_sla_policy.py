from __future__ import annotations


def response_sla_warnings(policy: dict[str, object]) -> tuple[str, ...]:
    warnings: list[str] = []
    p95 = policy.get("p95_latency_ms")
    error_rate = policy.get("max_error_rate_pct")
    if not isinstance(p95, int) or p95 <= 0:
        warnings.append("p95_latency_ms_must_be_positive")
    if not isinstance(error_rate, (int, float)) or not 0 <= error_rate <= 100:
        warnings.append("max_error_rate_pct_must_be_between_0_and_100")
    if policy.get("streaming_enabled") is not True:
        warnings.append("streaming_enabled_should_be_true_for_chat_sla")
    if not policy.get("owner"):
        warnings.append("owner_missing")
    return tuple(warnings)


def response_sla_is_ready(policy: dict[str, object]) -> bool:
    return not response_sla_warnings(policy)
