from __future__ import annotations


def fallback_policy_warnings(routes: dict[str, str | None], *, primary: str | None = None) -> tuple[str, ...]:
    warnings: list[str] = []
    if primary not in routes:
        warnings.append("primary_route_missing")
    for alias, fallback in routes.items():
        if fallback and fallback not in routes:
            warnings.append(f"{alias}_fallback_target_missing")
    for alias in routes:
        seen: set[str] = set()
        current: str | None = alias
        while current:
            if current in seen:
                warnings.append(f"{alias}_fallback_cycle_detected")
                break
            seen.add(current)
            current = routes.get(current)
    return tuple(dict.fromkeys(warnings))


def fallback_policy_is_valid(routes: dict[str, str | None], *, primary: str | None = None) -> bool:
    return not fallback_policy_warnings(routes, primary=primary)
