from __future__ import annotations

import re
from datetime import datetime


_ID = re.compile(r"[a-z0-9][a-z0-9-]*\Z")
_VERSION = re.compile(r"\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?\Z")
_DIGEST = re.compile(r"[0-9a-f]{64}\Z")


def _timestamp(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None and parsed.utcoffset() is not None else None


def prompt_template_contract_violations(template: dict[str, object]) -> tuple[str, ...]:
    violations: list[str] = []
    if not isinstance(template.get("template_id"), str) or not _ID.fullmatch(template["template_id"]):
        violations.append("template_id_must_be_a_stable_slug")
    if not isinstance(template.get("version"), str) or not _VERSION.fullmatch(template["version"]):
        violations.append("version_must_be_semver")
    if not isinstance(template.get("content_sha256"), str) or not _DIGEST.fullmatch(template["content_sha256"]):
        violations.append("content_sha256_is_invalid")
    if template.get("approved") is not True:
        violations.append("template_must_be_explicitly_approved")
    if _timestamp(template.get("reviewed_at")) is None:
        violations.append("reviewed_at_must_be_timezone_aware")
    return tuple(violations)


def prompt_template_contract_is_safe(template: dict[str, object]) -> bool:
    return not prompt_template_contract_violations(template)
