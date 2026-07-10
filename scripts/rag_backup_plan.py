#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys

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


def verification_report(
    targets: list[str] | tuple[str, ...] | set[str],
    checks: list[str] | tuple[str, ...] | set[str],
) -> dict[str, object]:
    missing_targets = missing_backup_targets(targets)
    missing_checks = missing_restore_checks(checks)
    return {
        "complete": not missing_targets and not missing_checks,
        "required_targets": list(REQUIRED_BACKUP_TARGETS),
        "required_restore_checks": list(REQUIRED_RESTORE_CHECKS),
        "missing_targets": list(missing_targets),
        "missing_restore_checks": list(missing_checks),
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate RAG vector backup verification coverage.")
    parser.add_argument("--target", action="append", default=[], help="Backup target covered by the plan.")
    parser.add_argument("--check", action="append", default=[], help="Restore verification check covered by the plan.")
    parser.add_argument("--json", action="store_true", help="Print a JSON report.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    report = verification_report(args.target, args.check)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    elif report["complete"]:
        print("RAG backup verification coverage is complete")
    else:
        for target in report["missing_targets"]:
            print(f"missing-target: {target}", file=sys.stderr)
        for check in report["missing_restore_checks"]:
            print(f"missing-restore-check: {check}", file=sys.stderr)
    return 0 if report["complete"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
