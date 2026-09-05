#!/usr/bin/env python3
"""Run an allowlisted set of offline RAG release gates from one manifest."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Callable


SCHEMA_VERSION = 1
MAX_CHECKS = 32
MAX_ARGUMENTS_PER_CHECK = 64
MAX_ARGUMENT_LENGTH = 4096
CHECK_ID_PATTERN = re.compile(r"[a-z][a-z0-9-]{0,63}\Z")
GATE_SCRIPTS = {
    "chat-retention": "chat_retention_policy_gate.py",
    "citation-freshness": "citation_freshness_release.py",
    "index-replica-consistency": "index_replica_consistency.py",
    "litellm-preflight": "litellm_preflight.py",
    "vector-backup": "rag_backup_plan.py",
}


class ManifestError(ValueError):
    """Raised when a release-check manifest violates the versioned contract."""


def load_manifest(path: Path) -> dict[str, object]:
    """Load and validate a v1 release-check manifest."""
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as error:
        raise ManifestError(f"unable to read manifest: {error}") from error
    except json.JSONDecodeError as error:
        raise ManifestError(f"manifest is not valid JSON: {error}") from error
    return validate_manifest(payload)


def validate_manifest(payload: object) -> dict[str, object]:
    """Return a normalized manifest or raise a stable validation error."""
    if not isinstance(payload, dict):
        raise ManifestError("manifest must be a JSON object")

    unexpected_root_fields = set(payload) - {"$schema", "schema_version", "checks"}
    if unexpected_root_fields:
        raise ManifestError(
            "manifest contains unsupported fields: "
            + ", ".join(sorted(unexpected_root_fields))
        )
    if payload.get("schema_version") != SCHEMA_VERSION or isinstance(
        payload.get("schema_version"), bool
    ):
        raise ManifestError(f"schema_version must be {SCHEMA_VERSION}")
    schema_reference = payload.get("$schema")
    if schema_reference is not None and (
        not isinstance(schema_reference, str) or not schema_reference.strip()
    ):
        raise ManifestError("$schema must be a non-empty string when provided")

    checks = payload.get("checks")
    if not isinstance(checks, list) or not checks:
        raise ManifestError("checks must be a non-empty JSON array")
    if len(checks) > MAX_CHECKS:
        raise ManifestError(f"checks cannot contain more than {MAX_CHECKS} entries")

    normalized_checks: list[dict[str, object]] = []
    seen_ids: set[str] = set()
    for index, check in enumerate(checks):
        if not isinstance(check, dict):
            raise ManifestError(f"checks[{index}] must be a JSON object")
        unexpected_fields = set(check) - {"id", "gate", "args"}
        if unexpected_fields:
            raise ManifestError(
                f"checks[{index}] contains unsupported fields: "
                + ", ".join(sorted(unexpected_fields))
            )

        check_id = check.get("id")
        if not isinstance(check_id, str) or not CHECK_ID_PATTERN.fullmatch(check_id):
            raise ManifestError(
                f"checks[{index}].id must match {CHECK_ID_PATTERN.pattern}"
            )
        if check_id in seen_ids:
            raise ManifestError(f"duplicate check id: {check_id}")
        seen_ids.add(check_id)

        gate = check.get("gate")
        if not isinstance(gate, str) or gate not in GATE_SCRIPTS:
            supported = ", ".join(sorted(GATE_SCRIPTS))
            raise ManifestError(
                f"checks[{index}].gate must be one of: {supported}"
            )

        args = check.get("args", [])
        if not isinstance(args, list):
            raise ManifestError(f"checks[{index}].args must be a JSON array")
        if len(args) > MAX_ARGUMENTS_PER_CHECK:
            raise ManifestError(
                f"checks[{index}].args cannot contain more than "
                f"{MAX_ARGUMENTS_PER_CHECK} entries"
            )
        for argument_index, argument in enumerate(args):
            if (
                not isinstance(argument, str)
                or "\x00" in argument
                or len(argument) > MAX_ARGUMENT_LENGTH
            ):
                raise ManifestError(
                    f"checks[{index}].args[{argument_index}] must be a string "
                    f"of at most {MAX_ARGUMENT_LENGTH} characters without null bytes"
                )

        normalized_checks.append({"id": check_id, "gate": gate, "args": args})

    return {"schema_version": SCHEMA_VERSION, "checks": normalized_checks}


def _decode_gate_report(stdout: str) -> dict[str, object]:
    try:
        report = json.loads(stdout)
    except json.JSONDecodeError as error:
        raise ValueError("gate did not emit valid JSON") from error
    if not isinstance(report, dict):
        raise ValueError("gate report must be a JSON object")
    return report


def run_release_checks(
    manifest: dict[str, object],
    *,
    manifest_directory: Path,
    timeout_seconds: int = 30,
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> dict[str, object]:
    """Execute validated checks without a shell and return one aggregate report."""
    if not isinstance(timeout_seconds, int) or isinstance(timeout_seconds, bool) or timeout_seconds < 1:
        raise ValueError("timeout_seconds must be a positive integer")

    script_directory = Path(__file__).resolve().parent
    results: list[dict[str, object]] = []
    checks = manifest["checks"]
    assert isinstance(checks, list)
    for check in checks:
        assert isinstance(check, dict)
        check_id = str(check["id"])
        gate = str(check["gate"])
        args = check["args"]
        assert isinstance(args, list)
        command = [
            sys.executable,
            str(script_directory / GATE_SCRIPTS[gate]),
            *[str(argument) for argument in args],
        ]
        result: dict[str, object] = {"gate": gate, "id": check_id}
        try:
            completed = runner(
                command,
                cwd=manifest_directory,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired:
            result.update(
                {
                    "error": f"gate exceeded {timeout_seconds} second timeout",
                    "status": "error",
                }
            )
        except OSError as error:
            result.update({"error": f"unable to execute gate: {error}", "status": "error"})
        else:
            result["exit_code"] = completed.returncode
            try:
                result["report"] = _decode_gate_report(completed.stdout)
            except ValueError as error:
                result.update({"error": str(error), "status": "error"})
            else:
                if completed.returncode == 0:
                    result["status"] = "pass"
                elif completed.returncode == 1:
                    result["status"] = "fail"
                else:
                    result["status"] = "error"
            if completed.stderr.strip():
                result["stderr"] = completed.stderr.strip()
        results.append(result)

    passed = sum(result["status"] == "pass" for result in results)
    failed = sum(result["status"] == "fail" for result in results)
    errors = sum(result["status"] == "error" for result in results)
    status = "error" if errors else "fail" if failed else "pass"
    return {
        "checks": results,
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "summary": {
            "errors": errors,
            "failed": failed,
            "passed": passed,
            "total": len(results),
        },
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run versioned, offline RAG release checks from one manifest."
    )
    parser.add_argument("manifest", type=Path, help="Path to a v1 release-check manifest")
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=30,
        help="Maximum runtime for each gate (default: 30)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        if args.timeout_seconds < 1:
            raise ManifestError("timeout_seconds must be a positive integer")
        manifest_path = args.manifest.resolve()
        manifest = load_manifest(manifest_path)
        report = run_release_checks(
            manifest,
            manifest_directory=manifest_path.parent,
            timeout_seconds=args.timeout_seconds,
        )
    except (ManifestError, ValueError) as error:
        print(json.dumps({"error": str(error), "status": "error"}, sort_keys=True), file=sys.stderr)
        return 2

    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "pass" else 1 if report["status"] == "fail" else 2


if __name__ == "__main__":
    raise SystemExit(main())
