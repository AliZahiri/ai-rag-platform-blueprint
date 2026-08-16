from __future__ import annotations

from datetime import datetime
import re


_SHA256 = re.compile(r"[0-9a-f]{64}\Z")


def source_manifest_violations(manifest: dict[str, object]) -> tuple[str, ...]:
    violations: list[str] = []
    if not isinstance(manifest.get("source_id"), str) or not manifest["source_id"].strip():
        violations.append("source_id_is_required")
    if not isinstance(manifest.get("content_sha256"), str) or not _SHA256.fullmatch(manifest["content_sha256"]):
        violations.append("content_sha256_is_invalid")
    value = manifest.get("retrieved_at")
    try:
        timestamp = datetime.fromisoformat(value.replace("Z", "+00:00")) if isinstance(value, str) else None
    except ValueError:
        timestamp = None
    if timestamp is None or timestamp.tzinfo is None or timestamp.utcoffset() is None:
        violations.append("retrieved_at_must_be_timezone_aware")
    if not isinstance(manifest.get("license"), str) or not manifest["license"].strip():
        violations.append("license_is_required")
    return tuple(violations)


def source_manifest_is_traceable(manifest: dict[str, object]) -> bool:
    return not source_manifest_violations(manifest)
