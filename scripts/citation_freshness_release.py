#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import date
import json
from pathlib import Path
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.citation_source_ids import citation_source_warnings
from scripts.source_freshness_policy import source_freshness_warnings


def citation_freshness_violations(sources: list[dict[str, object]], *, today: date, max_age_days: int = 180) -> tuple[str, ...]:
    if not isinstance(max_age_days, int) or isinstance(max_age_days, bool) or max_age_days <= 0:
        raise ValueError("maximum source age must be a positive integer")
    violations: list[str] = []
    if not sources:
        violations.append("at_least_one_citation_source_is_required")
    violations.extend(citation_source_warnings(sources))
    for index, source in enumerate(sources):
        raw_source_id = source.get("source_id")
        source_id = raw_source_id.strip() if isinstance(raw_source_id, str) else ""
        source_id = source_id or f"source_{index}"
        violations.extend(f"{source_id}:{warning}" for warning in source_freshness_warnings(source, today=today, max_age_days=max_age_days))
    return tuple(violations)


def citations_are_fresh_for_release(sources: list[dict[str, object]], *, today: date, max_age_days: int = 180) -> bool:
    return not citation_freshness_violations(sources, today=today, max_age_days=max_age_days)


def citation_freshness_report(
    sources: list[dict[str, object]],
    *,
    today: date,
    max_age_days: int = 180,
) -> dict[str, object]:
    violations = citation_freshness_violations(sources, today=today, max_age_days=max_age_days)
    return {
        "release_allowed": not violations,
        "source_count": len(sources),
        "evaluated_on": today.isoformat(),
        "max_age_days": max_age_days,
        "violations": list(violations),
    }


def load_sources(path: Path) -> list[dict[str, object]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("citation source input must be a JSON array")

    sources: list[dict[str, object]] = []
    for index, item in enumerate(payload):
        if not isinstance(item, dict):
            raise ValueError(f"citation source {index} must be a JSON object")
        source = dict(item)
        reviewed_at = source.get("last_reviewed_at")
        if isinstance(reviewed_at, str):
            try:
                source["last_reviewed_at"] = date.fromisoformat(reviewed_at)
            except ValueError:
                pass
        sources.append(source)
    return sources


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate citation freshness before releasing a RAG answer.")
    parser.add_argument("input", type=Path, help="JSON array containing citation source metadata.")
    parser.add_argument("--today", required=True, type=date.fromisoformat, help="Evaluation date in YYYY-MM-DD format.")
    parser.add_argument("--max-age-days", type=int, default=180, help="Maximum accepted source review age.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        report = citation_freshness_report(
            load_sources(args.input),
            today=args.today,
            max_age_days=args.max_age_days,
        )
    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["release_allowed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
