from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
import sys


def _timestamp(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None and parsed.utcoffset() is not None else None


def evaluation_dataset_provenance_violations(cases: list[dict[str, object]], *, now: datetime, maximum_review_age_days: int = 180) -> tuple[str, ...]:
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("current time must be timezone-aware")
    if not isinstance(maximum_review_age_days, int) or isinstance(maximum_review_age_days, bool) or maximum_review_age_days <= 0:
        raise ValueError("maximum review age must be positive")
    if not cases:
        return ("at_least_one_evaluation_case_is_required",)

    violations: list[str] = []
    seen_case_ids: set[str] = set()
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            violations.append(f"case_{index}:must_be_an_object")
            continue
        case_id = case.get("case_id")
        if not isinstance(case_id, str) or not case_id.strip():
            violations.append(f"case_{index}:case_id_is_required")
        elif case_id in seen_case_ids:
            violations.append(f"case_{index}:case_id_must_be_unique")
        seen_case_ids.add(case_id)
        if not isinstance(case.get("source_snapshot"), str) or not case["source_snapshot"].strip():
            violations.append(f"case_{index}:source_snapshot_is_required")
        if not isinstance(case.get("expected_answer"), str) or not case["expected_answer"].strip():
            violations.append(f"case_{index}:expected_answer_is_required")
        source_ids = case.get("source_ids")
        if not isinstance(source_ids, list) or not source_ids or not all(isinstance(source_id, str) and source_id.strip() for source_id in source_ids) or len(set(source_ids)) != len(source_ids):
            violations.append(f"case_{index}:source_ids_must_be_a_unique_non_empty_string_list")
        reviewed_at = _timestamp(case.get("reviewed_at"))
        if reviewed_at is None or (now - reviewed_at).total_seconds() < 0 or (now - reviewed_at).days > maximum_review_age_days:
            violations.append(f"case_{index}:review_is_not_within_age_budget")
    return tuple(violations)


def evaluation_dataset_provenance_is_complete(cases: list[dict[str, object]], **policy: object) -> bool:
    return not evaluation_dataset_provenance_violations(cases, **policy)


def load_evaluation_cases(path: Path) -> list[dict[str, object]]:
    """Load evaluation evidence without accepting an ambiguous top-level shape."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("evaluation provenance input must be a JSON object")
    cases = payload.get("cases")
    if not isinstance(cases, list):
        raise ValueError("cases must be a JSON array")
    return cases


def evaluation_dataset_provenance_report(
    cases: list[dict[str, object]], *, now: datetime, maximum_review_age_days: int
) -> dict[str, object]:
    violations = evaluation_dataset_provenance_violations(
        cases, now=now, maximum_review_age_days=maximum_review_age_days
    )
    return {
        "case_count": len(cases),
        "maximum_review_age_days": maximum_review_age_days,
        "status": "pass" if not violations else "fail",
        "violations": list(violations),
    }


def _parse_now(value: str) -> datetime:
    parsed = _timestamp(value)
    if parsed is None:
        raise ValueError("now must be an ISO-8601 timestamp with a timezone")
    return parsed


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate traceable, recently reviewed RAG evaluation evidence."
    )
    parser.add_argument("evidence", type=Path, help="JSON object containing a cases array")
    parser.add_argument(
        "--now",
        required=True,
        help="Timezone-aware ISO-8601 release timestamp used for deterministic review-age checks",
    )
    parser.add_argument(
        "--maximum-review-age-days", type=int, default=180,
        help="Maximum permitted age of an evaluation-case review (default: 180)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        report = evaluation_dataset_provenance_report(
            load_evaluation_cases(args.evidence),
            now=_parse_now(args.now),
            maximum_review_age_days=args.maximum_review_age_days,
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
        print(json.dumps({"error": str(error), "status": "error"}, sort_keys=True), file=sys.stderr)
        return 2

    print(json.dumps(report, sort_keys=True))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
