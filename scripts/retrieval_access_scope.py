from __future__ import annotations


def retrieval_access_scope_violations(
    records: list[dict[str, object]], *, tenant: str, required_scope: str
) -> tuple[str, ...]:
    if not isinstance(tenant, str) or not tenant.strip():
        raise ValueError("tenant must be a non-empty string")
    if not isinstance(required_scope, str) or not required_scope.strip():
        raise ValueError("required scope must be a non-empty string")
    if not records:
        return ("at_least_one_retrieval_record_is_required",)

    violations: list[str] = []
    seen_chunk_ids: set[str] = set()
    for index, record in enumerate(records):
        chunk_id = record.get("chunk_id")
        if not isinstance(chunk_id, str) or not chunk_id.strip():
            violations.append(f"record_{index}:chunk_id_is_required")
        elif chunk_id in seen_chunk_ids:
            violations.append(f"record_{index}:chunk_id_must_be_unique")
        seen_chunk_ids.add(chunk_id)

        if record.get("tenant") != tenant:
            violations.append(f"record_{index}:tenant_must_match_request")
        scopes = record.get("scopes")
        if not isinstance(scopes, list) or not all(isinstance(scope, str) and scope.strip() for scope in scopes):
            violations.append(f"record_{index}:scopes_must_be_a_non_empty_string_list")
        elif required_scope not in scopes:
            violations.append(f"record_{index}:required_scope_is_missing")
        if record.get("access_decision") != "granted":
            violations.append(f"record_{index}:access_must_be_granted")
    return tuple(violations)


def retrieval_access_scope_is_safe(
    records: list[dict[str, object]], *, tenant: str, required_scope: str
) -> bool:
    return not retrieval_access_scope_violations(records, tenant=tenant, required_scope=required_scope)
