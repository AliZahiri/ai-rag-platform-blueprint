from __future__ import annotations


def vector_index_capacity_violations(observations: list[dict[str, object]], *, maximum_utilization: float = 0.85) -> tuple[str, ...]:
    if not isinstance(maximum_utilization, (int, float)) or isinstance(maximum_utilization, bool) or not 0 < maximum_utilization <= 1:
        raise ValueError("maximum utilization must be between zero and one")
    if not observations:
        return ("at_least_one_collection_observation_is_required",)
    violations: list[str] = []
    seen_names: set[str] = set()
    for index, observation in enumerate(observations):
        name = observation.get("collection")
        if not isinstance(name, str) or not name.strip():
            violations.append(f"collection_{index}:name_is_required")
        elif name in seen_names:
            violations.append(f"collection_{index}:name_must_be_unique")
        seen_names.add(name)
        vectors, capacity = observation.get("vector_count"), observation.get("capacity")
        if not isinstance(vectors, int) or isinstance(vectors, bool) or vectors < 0:
            violations.append(f"collection_{index}:vector_count_must_be_non_negative")
        if not isinstance(capacity, int) or isinstance(capacity, bool) or capacity <= 0:
            violations.append(f"collection_{index}:capacity_must_be_positive")
        elif isinstance(vectors, int) and not isinstance(vectors, bool) and vectors / capacity > maximum_utilization:
            violations.append(f"collection_{index}:utilization_exceeds_budget")
        shards = observation.get("shard_count")
        if not isinstance(shards, int) or isinstance(shards, bool) or shards <= 0:
            violations.append(f"collection_{index}:shard_count_must_be_positive")
    return tuple(violations)


def vector_index_capacity_is_safe(observations: list[dict[str, object]], **policy: object) -> bool:
    return not vector_index_capacity_violations(observations, **policy)
