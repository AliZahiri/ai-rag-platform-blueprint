#!/usr/bin/env python3
"""Validate that Compose image defaults and their environment overrides are digest-pinned."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re


_COMPOSE_IMAGE = re.compile(
    r"^\s*image:\s*\$\{(?P<variable>[A-Z][A-Z0-9_]*):-(?P<image>[^}\s]+)\}\s*(?:#.*)?$"
)
_ENV_ASSIGNMENT = re.compile(r"^(?P<variable>[A-Z][A-Z0-9_]*)=(?P<value>[^\r\n]*)$")
_DIGEST_IMAGE = re.compile(r"[a-z0-9][a-z0-9._/-]*@sha256:[0-9a-f]{64}\Z")


def load_environment(path: Path) -> dict[str, str]:
    """Load the simple KEY=value environment-file subset used by this blueprint."""
    values: dict[str, str] = {}
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        match = _ENV_ASSIGNMENT.fullmatch(line)
        if match is None:
            raise ValueError(f"environment line {line_number} must use KEY=value syntax")
        variable, value = match.group("variable"), match.group("value")
        if variable in values:
            raise ValueError(f"environment variable is duplicated: {variable}")
        values[variable] = value
    return values


def compose_image_pinning_violations(compose_text: str, environment: dict[str, str]) -> tuple[str, ...]:
    """Return deterministic violations for image defaults and matching environment values."""
    violations: list[str] = []
    image_variables: set[str] = set()

    for line_number, line in enumerate(compose_text.splitlines(), start=1):
        if not line.lstrip().startswith("image:"):
            continue
        match = _COMPOSE_IMAGE.fullmatch(line)
        if match is None:
            violations.append(f"line_{line_number}:image_must_use_a_variable_with_a_digest_default")
            continue

        variable, default_image = match.group("variable"), match.group("image")
        if variable in image_variables:
            violations.append(f"line_{line_number}:image_variable_is_duplicated:{variable}")
        image_variables.add(variable)
        if _DIGEST_IMAGE.fullmatch(default_image) is None:
            violations.append(f"line_{line_number}:default_image_is_not_digest_pinned")

        environment_image = environment.get(variable)
        if environment_image is None:
            violations.append(f"{variable}:environment_override_is_missing")
        elif _DIGEST_IMAGE.fullmatch(environment_image) is None:
            violations.append(f"{variable}:environment_image_is_not_digest_pinned")
        elif environment_image != default_image:
            violations.append(f"{variable}:environment_image_does_not_match_compose_default")

    if not image_variables:
        violations.append("at_least_one_compose_image_is_required")
    return tuple(violations)


def validate_files(compose_path: Path, environment_path: Path) -> tuple[str, ...]:
    """Load the project files and return any image-pinning policy violations."""
    return compose_image_pinning_violations(
        compose_path.read_text(encoding="utf-8"), load_environment(environment_path)
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compose", type=Path, required=True, help="Docker Compose YAML file")
    parser.add_argument("--env", type=Path, required=True, help="Environment example file")
    parser.add_argument("--json", action="store_true", help="Emit a machine-readable report")
    args = parser.parse_args(argv)

    try:
        violations = validate_files(args.compose, args.env)
    except (OSError, UnicodeDecodeError, ValueError) as error:
        report = {"error": str(error), "status": "error"}
        exit_code = 2
    else:
        report = {
            "status": "rejected" if violations else "passed",
            "violations": list(violations),
        }
        exit_code = 1 if violations else 0

    if args.json:
        print(json.dumps(report, sort_keys=True))
    else:
        print(report["status"])
        for violation in report.get("violations", []):
            print(f"- {violation}")
        if "error" in report:
            print(f"- {report['error']}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
