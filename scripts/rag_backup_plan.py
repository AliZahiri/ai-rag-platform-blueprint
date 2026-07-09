#!/usr/bin/env python3
from __future__ import annotations

REQUIRED_BACKUP_TARGETS = (
    "vector_collections",
    "source_documents",
    "collection_metadata",
    "parser_config",
    "embedding_model_metadata",
    "collection_schema",
    "index_settings",
)

REQUIRED_RESTORE_CHECKS = (
    "collection_exists",
    "collection_schema_matches",
    "source_document_count_matches",
    "sample_similarity_query",
    "embedding_model_metadata_matches",
)


def missing_backup_targets(selected: list[str] | tuple[str, ...] | set[str]) -> tuple[str, ...]:
    selected_targets = set(selected)
    return tuple(target for target in REQUIRED_BACKUP_TARGETS if target not in selected_targets)


def missing_restore_checks(selected: list[str] | tuple[str, ...] | set[str]) -> tuple[str, ...]:
    selected_checks = set(selected)
    return tuple(check for check in REQUIRED_RESTORE_CHECKS if check not in selected_checks)


def backup_plan_is_complete(selected: list[str] | tuple[str, ...] | set[str]) -> bool:
    return not missing_backup_targets(selected)


def backup_verification_is_complete(
    targets: list[str] | tuple[str, ...] | set[str],
    checks: list[str] | tuple[str, ...] | set[str],
) -> bool:
    return not missing_backup_targets(targets) and not missing_restore_checks(checks)
