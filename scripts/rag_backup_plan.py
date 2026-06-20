#!/usr/bin/env python3
from __future__ import annotations

REQUIRED_BACKUP_TARGETS = (
    "vector_collections",
    "source_documents",
    "parser_config",
    "embedding_model_metadata",
    "collection_schema",
    "index_settings",
)


def missing_backup_targets(selected: list[str] | tuple[str, ...] | set[str]) -> tuple[str, ...]:
    selected_targets = set(selected)
    return tuple(target for target in REQUIRED_BACKUP_TARGETS if target not in selected_targets)


def backup_plan_is_complete(selected: list[str] | tuple[str, ...] | set[str]) -> bool:
    return not missing_backup_targets(selected)
