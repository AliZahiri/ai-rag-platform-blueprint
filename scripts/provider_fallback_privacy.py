from __future__ import annotations


def provider_fallback_privacy_violations(routes: list[dict[str, object]], *, allowed_regions: tuple[str, ...], maximum_retention_days: int = 30) -> tuple[str, ...]:
    regions = {value.strip().lower() for value in allowed_regions if isinstance(value, str) and value.strip()}
    if not regions:
        raise ValueError("allowed_regions must contain non-empty strings")
    if not isinstance(maximum_retention_days, int) or isinstance(maximum_retention_days, bool) or maximum_retention_days < 0:
        raise ValueError("maximum_retention_days must be non-negative")
    if not isinstance(routes, list) or not routes:
        return ("at_least_one_provider_route_is_required",)

    violations: list[str] = []
    route_ids: set[str] = set()
    for route_index, route in enumerate(routes):
        prefix = f"route_{route_index}"
        if not isinstance(route, dict):
            violations.append(f"{prefix}:must_be_an_object")
            continue
        route_id = route.get("route_id")
        if not isinstance(route_id, str) or not route_id.strip():
            violations.append(f"{prefix}:route_id_is_required")
        elif route_id in route_ids:
            violations.append(f"{prefix}:route_id_must_be_unique")
        else:
            route_ids.add(route_id)
        providers = route.get("providers")
        if not isinstance(providers, list) or len(providers) < 2:
            violations.append(f"{prefix}:primary_and_fallback_providers_are_required")
            continue
        provider_ids: set[str] = set()
        for provider_index, provider in enumerate(providers):
            provider_prefix = f"{prefix}:provider_{provider_index}"
            if not isinstance(provider, dict):
                violations.append(f"{provider_prefix}:must_be_an_object")
                continue
            provider_id = provider.get("provider_id")
            if not isinstance(provider_id, str) or not provider_id.strip():
                violations.append(f"{provider_prefix}:provider_id_is_required")
            elif provider_id in provider_ids:
                violations.append(f"{provider_prefix}:provider_id_must_be_unique_within_route")
            else:
                provider_ids.add(provider_id)
            region = provider.get("region")
            if not isinstance(region, str) or region.strip().lower() not in regions:
                violations.append(f"{provider_prefix}:region_is_not_approved")
            retention = provider.get("retention_days")
            if not isinstance(retention, int) or isinstance(retention, bool) or not 0 <= retention <= maximum_retention_days:
                violations.append(f"{provider_prefix}:retention_exceeds_policy")
            if provider.get("training_use_permitted") is not False:
                violations.append(f"{provider_prefix}:training_use_must_be_disabled")
    return tuple(violations)


def provider_fallback_privacy_is_safe(routes: list[dict[str, object]], **policy: object) -> bool:
    return not provider_fallback_privacy_violations(routes, **policy)
