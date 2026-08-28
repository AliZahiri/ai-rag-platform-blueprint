from __future__ import annotations

import math


def usage_reconciliation_violations(records: list[dict[str, object]], provider: dict[str, object], *, maximum_token_delta: int = 0, maximum_cost_delta_usd: float = 0.01) -> tuple[str, ...]:
    if not isinstance(maximum_token_delta, int) or isinstance(maximum_token_delta, bool) or maximum_token_delta < 0:
        raise ValueError("maximum token delta must be a non-negative integer")
    if not isinstance(maximum_cost_delta_usd, (int, float)) or isinstance(maximum_cost_delta_usd, bool) or not math.isfinite(maximum_cost_delta_usd) or maximum_cost_delta_usd < 0:
        raise ValueError("maximum cost delta must be finite and non-negative")
    if not isinstance(records, list) or not records:
        return ("at_least_one_gateway_usage_record_is_required",)
    violations: list[str] = []
    seen: set[str] = set()
    gateway_input = gateway_output = 0
    gateway_cost = 0.0
    for index, record in enumerate(records):
        request_id = record.get("request_id") if isinstance(record, dict) else None
        if not isinstance(request_id, str) or not request_id.strip():
            violations.append(f"record_{index}:request_id_is_required")
        elif request_id in seen:
            violations.append(f"record_{index}:request_id_must_be_unique")
        else:
            seen.add(request_id)
        for field in ("input_tokens", "output_tokens"):
            value = record.get(field) if isinstance(record, dict) else None
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                violations.append(f"record_{index}:{field}_must_be_non_negative")
            elif field == "input_tokens":
                gateway_input += value
            else:
                gateway_output += value
        cost = record.get("cost_usd") if isinstance(record, dict) else None
        if not isinstance(cost, (int, float)) or isinstance(cost, bool) or not math.isfinite(cost) or cost < 0:
            violations.append(f"record_{index}:cost_usd_must_be_finite_and_non_negative")
        else:
            gateway_cost += float(cost)
    expected = {"request_count": len(records), "input_tokens": gateway_input, "output_tokens": gateway_output}
    for field, actual in expected.items():
        value = provider.get(field)
        delta = 0 if field == "request_count" else maximum_token_delta
        if not isinstance(value, int) or isinstance(value, bool) or abs(value - actual) > delta:
            violations.append(f"provider_{field}_does_not_reconcile")
    provider_cost = provider.get("cost_usd")
    if not isinstance(provider_cost, (int, float)) or isinstance(provider_cost, bool) or not math.isfinite(provider_cost) or abs(float(provider_cost) - gateway_cost) > maximum_cost_delta_usd:
        violations.append("provider_cost_usd_does_not_reconcile")
    return tuple(violations)


def usage_reconciles(records: list[dict[str, object]], provider: dict[str, object], **policy: object) -> bool:
    return not usage_reconciliation_violations(records, provider, **policy)
