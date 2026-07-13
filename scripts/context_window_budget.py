from __future__ import annotations


def context_budget_warnings(chunk_tokens: list[int], *, max_context_tokens: int, reserved_output_tokens: int) -> tuple[str, ...]:
    warnings: list[str] = []
    if max_context_tokens <= 0:
        warnings.append("max_context_tokens_must_be_positive")
    if reserved_output_tokens < 0:
        warnings.append("reserved_output_tokens_must_not_be_negative")
    if any(not isinstance(tokens, int) or tokens < 0 for tokens in chunk_tokens):
        warnings.append("chunk_tokens_must_be_non_negative_integers")
    if warnings:
        return tuple(warnings)
    if sum(chunk_tokens) + reserved_output_tokens > max_context_tokens:
        warnings.append("retrieved_context_exceeds_route_budget")
    return tuple(warnings)


def context_budget_is_safe(chunk_tokens: list[int], *, max_context_tokens: int, reserved_output_tokens: int) -> bool:
    return not context_budget_warnings(
        chunk_tokens,
        max_context_tokens=max_context_tokens,
        reserved_output_tokens=reserved_output_tokens,
    )
