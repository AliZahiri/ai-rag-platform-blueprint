from __future__ import annotations

import re


_OPAQUE_ID = re.compile(r"[0-9a-f]{32,64}\Z")


def evaluation_leakage_violations(training_ids: list[str], holdout_ids: list[str], *, minimum_holdout_size: int = 20) -> tuple[str, ...]:
    if not isinstance(minimum_holdout_size, int) or isinstance(minimum_holdout_size, bool) or minimum_holdout_size < 1:
        raise ValueError("minimum_holdout_size must be a positive integer")
    violations: list[str] = []
    for label, identifiers in (("training", training_ids), ("holdout", holdout_ids)):
        if not isinstance(identifiers, list) or any(not isinstance(item, str) or not _OPAQUE_ID.fullmatch(item) for item in identifiers):
            violations.append(f"{label}_ids_must_be_opaque_hex_identifiers")
            continue
        if len(set(identifiers)) != len(identifiers):
            violations.append(f"{label}_ids_must_be_unique")
    if isinstance(holdout_ids, list) and len(holdout_ids) < minimum_holdout_size:
        violations.append("holdout_size_is_below_minimum")
    if isinstance(training_ids, list) and isinstance(holdout_ids, list) and set(training_ids).intersection(holdout_ids):
        violations.append("training_and_holdout_ids_overlap")
    return tuple(violations)


def evaluation_holdout_is_isolated(training_ids: list[str], holdout_ids: list[str], **policy: object) -> bool:
    return not evaluation_leakage_violations(training_ids, holdout_ids, **policy)
