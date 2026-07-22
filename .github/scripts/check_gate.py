from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Iterable


def evaluate_check_runs(
    payload: dict[str, object],
    *,
    required_names: Iterable[str],
) -> tuple[str, tuple[str, ...]]:
    runs = payload.get("statusCheckRollup", [])
    if not isinstance(runs, list):
        return "failed", ("invalid_check_run_payload",)

    missing: list[str] = []
    pending: list[str] = []
    failed: list[str] = []
    for name in required_names:
        matching = [
            run for run in runs if isinstance(run, dict) and run.get("name") == name
        ]
        if not matching:
            missing.append(name)
            continue
        if any(str(run.get("status", "")).lower() != "completed" for run in matching):
            pending.append(name)
            continue
        if any(
            str(run.get("conclusion", "")).lower() != "success"
            for run in matching
        ):
            failed.append(name)

    if failed:
        return "failed", tuple(failed)
    if missing or pending:
        details = tuple(f"missing:{name}" for name in missing) + tuple(
            f"pending:{name}" for name in pending
        )
        return "pending", details
    return "ready", ()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate PR-associated GitHub check runs.")
    parser.add_argument("--required", required=True)
    args = parser.parse_args(argv)

    required_names = tuple(
        name.strip() for name in args.required.split(",") if name.strip()
    )
    if not required_names:
        print("failed: no required check names configured")
        return 2

    payload = json.load(sys.stdin)
    state, details = evaluate_check_runs(
        payload,
        required_names=required_names,
    )
    suffix = f": {', '.join(details)}" if details else ""
    print(f"{state}{suffix}")
    return {"ready": 0, "pending": 1, "failed": 2}[state]


if __name__ == "__main__":
    raise SystemExit(main())
