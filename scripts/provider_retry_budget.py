from __future__ import annotations


def provider_retry_violations(attempts: list[dict[str, object]], *, maximum_attempts: int = 3, maximum_delay_ms: int = 5000) -> tuple[str, ...]:
    if not isinstance(maximum_attempts, int) or isinstance(maximum_attempts, bool) or maximum_attempts < 1:
        raise ValueError("maximum_attempts must be a positive integer")
    if not isinstance(maximum_delay_ms, int) or isinstance(maximum_delay_ms, bool) or maximum_delay_ms < 0:
        raise ValueError("maximum_delay_ms must be a non-negative integer")
    if not isinstance(attempts, list) or not attempts:
        return ("at_least_one_attempt_is_required",)
    violations: list[str] = []
    request_ids = {item.get("request_id") for item in attempts if isinstance(item, dict)}
    if len(request_ids) != 1 or not all(isinstance(item, str) and item.strip() for item in request_ids):
        violations.append("attempts_must_share_one_request_id")
    if len(attempts) > maximum_attempts:
        violations.append("attempt_count_exceeds_budget")
    total_delay = 0
    for index, attempt in enumerate(attempts, start=1):
        if not isinstance(attempt, dict):
            violations.append(f"attempt_{index}:must_be_an_object")
            continue
        if attempt.get("attempt") != index:
            violations.append(f"attempt_{index}:sequence_is_invalid")
        if not isinstance(attempt.get("provider"), str) or not attempt["provider"].strip():
            violations.append(f"attempt_{index}:provider_is_required")
        status = attempt.get("status_code")
        if not isinstance(status, int) or isinstance(status, bool) or not 100 <= status <= 599:
            violations.append(f"attempt_{index}:status_code_is_invalid")
        delay = attempt.get("delay_before_ms")
        if not isinstance(delay, int) or isinstance(delay, bool) or delay < 0:
            violations.append(f"attempt_{index}:delay_before_ms_is_invalid")
        else:
            total_delay += delay
        if index < len(attempts) and isinstance(status, int) and status != 429 and status < 500:
            violations.append(f"attempt_{index}:non_retryable_status_was_retried")
    if total_delay > maximum_delay_ms:
        violations.append("cumulative_retry_delay_exceeds_budget")
    return tuple(violations)


def provider_retry_is_bounded(attempts: list[dict[str, object]], **policy: object) -> bool:
    return not provider_retry_violations(attempts, **policy)
