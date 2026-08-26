from __future__ import annotations


def query_expansion_budget_violations(
    original_query: object,
    expanded_queries: object,
    *,
    max_expansions: int = 4,
    max_query_chars: int = 512,
) -> tuple[str, ...]:
    """Validate deterministic bounds for retrieval query expansion."""
    if not isinstance(max_expansions, int) or isinstance(max_expansions, bool) or max_expansions < 1:
        raise ValueError("max_expansions must be a positive integer")
    if not isinstance(max_query_chars, int) or isinstance(max_query_chars, bool) or max_query_chars < 1:
        raise ValueError("max_query_chars must be a positive integer")

    violations: list[str] = []
    original = original_query.strip() if isinstance(original_query, str) else ""
    if not original:
        violations.append("original_query_is_required")
    elif len(original) > max_query_chars:
        violations.append("original_query_exceeds_character_budget")

    if not isinstance(expanded_queries, list) or not expanded_queries:
        violations.append("expanded_queries_must_be_a_non_empty_list")
        return tuple(violations)
    if len(expanded_queries) > max_expansions:
        violations.append("expanded_query_count_exceeds_budget")

    seen: set[str] = set()
    for index, query in enumerate(expanded_queries):
        if not isinstance(query, str) or not query.strip():
            violations.append(f"expanded_query_{index}:query_is_required")
            continue
        normalized = query.strip().casefold()
        if len(query.strip()) > max_query_chars:
            violations.append(f"expanded_query_{index}:query_exceeds_character_budget")
        if normalized in seen:
            violations.append(f"expanded_query_{index}:query_must_be_unique")
        else:
            seen.add(normalized)

    if original and original.casefold() not in seen:
        violations.append("original_query_must_be_preserved")
    return tuple(violations)


def query_expansion_is_within_budget(original_query: object, expanded_queries: object, **policy: object) -> bool:
    return not query_expansion_budget_violations(original_query, expanded_queries, **policy)
