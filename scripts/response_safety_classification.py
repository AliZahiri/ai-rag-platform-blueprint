from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


_ALLOWED = {"safe", "review", "blocked"}


def response_safety_classification_violations(records: list[dict[str, object]], *, minimum_safe_confidence: float = 0.8) -> tuple[str, ...]:
    if not isinstance(minimum_safe_confidence, (int, float)) or isinstance(minimum_safe_confidence, bool) or not 0 < minimum_safe_confidence <= 1:
        raise ValueError("minimum safe confidence must be between zero and one")
    if not records:
        return ("at_least_one_response_record_is_required",)
    violations: list[str] = []
    seen_ids: set[str] = set()
    for index, record in enumerate(records):
        response_id = record.get("response_id")
        if not isinstance(response_id, str) or not response_id.strip():
            violations.append(f"record_{index}:response_id_is_required")
        elif response_id in seen_ids:
            violations.append(f"record_{index}:response_id_must_be_unique")
        else:
            seen_ids.add(response_id)
        classification = record.get("classification")
        if not isinstance(classification, str) or classification not in _ALLOWED:
            violations.append(f"record_{index}:classification_is_invalid")
        confidence = record.get("confidence")
        if not isinstance(confidence, (int, float)) or isinstance(confidence, bool) or not 0 <= confidence <= 1:
            violations.append(f"record_{index}:confidence_must_be_between_zero_and_one")
        elif classification == "safe" and confidence < minimum_safe_confidence:
            violations.append(f"record_{index}:safe_classification_confidence_is_too_low")
        if record.get("release") is not (classification == "safe"):
            violations.append(f"record_{index}:release_decision_must_match_classification")
    return tuple(violations)


def response_safety_classification_is_safe(records: list[dict[str, object]], **policy: object) -> bool:
    return not response_safety_classification_violations(records, **policy)


def load_response_records(path: Path) -> list[dict[str, object]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("response safety input must be a JSON array")
    if any(not isinstance(record, dict) for record in payload):
        raise ValueError("every response safety record must be a JSON object")
    return payload


def response_safety_report(
    records: list[dict[str, object]],
    *,
    minimum_safe_confidence: float = 0.8,
) -> dict[str, object]:
    violations = response_safety_classification_violations(
        records,
        minimum_safe_confidence=minimum_safe_confidence,
    )
    return {
        "minimum_safe_confidence": minimum_safe_confidence,
        "record_count": len(records),
        "status": "pass" if not violations else "fail",
        "violations": list(violations),
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate offline response-safety classification evidence."
    )
    parser.add_argument("evidence", type=Path, help="JSON array of response records")
    parser.add_argument("--minimum-safe-confidence", type=float, default=0.8)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        report = response_safety_report(
            load_response_records(args.evidence),
            minimum_safe_confidence=args.minimum_safe_confidence,
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
        print(json.dumps({"error": str(error), "status": "error"}), file=sys.stderr)
        return 2

    print(json.dumps(report, sort_keys=True))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
