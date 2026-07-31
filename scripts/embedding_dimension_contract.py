from __future__ import annotations


def embedding_dimension_violations(bindings: list[dict[str, object]]) -> tuple[str, ...]:
    if not bindings:
        return ("at_least_one_embedding_binding_is_required",)
    violations: list[str] = []
    seen_routes: set[str] = set()
    for index, binding in enumerate(bindings):
        route = str(binding.get("route", "")).strip()
        if not route:
            violations.append(f"binding_{index}:route_is_required")
        elif route in seen_routes:
            violations.append(f"binding_{index}:route_must_be_unique")
        seen_routes.add(route)
        for field in ("provider", "model", "index"):
            if not str(binding.get(field, "")).strip():
                violations.append(f"binding_{index}:{field}_is_required")
        output_dimension = binding.get("output_dimension")
        index_dimension = binding.get("index_dimension")
        for field, value in (("output_dimension", output_dimension), ("index_dimension", index_dimension)):
            if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
                violations.append(f"binding_{index}:{field}_must_be_a_positive_integer")
        if (isinstance(output_dimension, int) and not isinstance(output_dimension, bool) and output_dimension > 0 and isinstance(index_dimension, int) and not isinstance(index_dimension, bool) and index_dimension > 0 and output_dimension != index_dimension):
            violations.append(f"binding_{index}:embedding_and_index_dimensions_must_match")
    return tuple(violations)


def embedding_bindings_are_compatible(bindings: list[dict[str, object]]) -> bool:
    return not embedding_dimension_violations(bindings)
