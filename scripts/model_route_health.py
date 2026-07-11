from __future__ import annotations

REQUIRED_ROUTE_FIELDS = ("alias", "provider", "model")
REQUIRED_LIMITS = ("timeout_seconds", "max_retries")
REQUIRED_CAPABILITIES = ("streaming", "json_mode")


def route_health_warnings(route: dict[str, object], known_aliases: set[str] | None = None) -> tuple[str, ...]:
    aliases = set() if known_aliases is None else known_aliases
    warnings: list[str] = []
    for field in REQUIRED_ROUTE_FIELDS:
        if not str(route.get(field, "")).strip():
            warnings.append(f"{field}_is_required")

    limits = route.get("limits")
    if not isinstance(limits, dict):
        warnings.append("limits_must_be_object")
    else:
        for field in REQUIRED_LIMITS:
            value = limits.get(field)
            if not isinstance(value, (int, float)) or value <= 0:
                warnings.append(f"limits_{field}_must_be_positive")

    capabilities = route.get("capabilities")
    if not isinstance(capabilities, dict):
        warnings.append("capabilities_must_be_object")
    else:
        for field in REQUIRED_CAPABILITIES:
            if capabilities.get(field) is not True:
                warnings.append(f"capabilities_{field}_must_be_true")

    fallback = str(route.get("fallback", "")).strip()
    if fallback and fallback not in aliases:
        warnings.append("fallback_alias_is_unknown")
    return tuple(warnings)


def route_health_is_ready(route: dict[str, object], known_aliases: set[str] | None = None) -> bool:
    return not route_health_warnings(route, known_aliases)
