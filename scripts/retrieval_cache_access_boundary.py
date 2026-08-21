from __future__ import annotations


def retrieval_cache_access_violations(
    entry: dict[str, object], *, tenant: str, required_scope: str
) -> tuple[str, ...]:
    if not isinstance(tenant, str) or not tenant.strip():
        raise ValueError("tenant must be a non-empty string")
    if not isinstance(required_scope, str) or not required_scope.strip():
        raise ValueError("required_scope must be a non-empty string")

    violations: list[str] = []
    if not isinstance(entry.get("cache_key"), str) or not entry["cache_key"].strip():
        violations.append("cache_key_is_required")
    if entry.get("tenant") != tenant:
        violations.append("cache_tenant_must_match_request")
    scopes = entry.get("scopes")
    if not isinstance(scopes, list) or not scopes or not all(
        isinstance(scope, str) and scope.strip() for scope in scopes
    ):
        violations.append("cache_scopes_must_be_a_non_empty_string_list")
    elif required_scope not in scopes:
        violations.append("required_scope_is_missing_from_cache_entry")
    if entry.get("access_decision") != "granted":
        violations.append("cache_access_must_be_granted")
    return tuple(violations)


def retrieval_cache_access_is_safe(
    entry: dict[str, object], *, tenant: str, required_scope: str
) -> bool:
    return not retrieval_cache_access_violations(
        entry, tenant=tenant, required_scope=required_scope
    )
