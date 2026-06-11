from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from pathlib import Path


MARKER_TEMPLATE = "<!-- daily-pr-task: {task_id} -->"
BRANCH_PREFIX = "daily/"


def load_tasks(backlog_path: Path) -> list[dict[str, str]]:
    data = json.loads(backlog_path.read_text(encoding="utf-8"))
    tasks = data["tasks"] if isinstance(data, dict) else data
    for task in tasks:
        task_id = task.get("id", "")
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", task_id):
            raise ValueError(f"invalid task id: {task_id}")
        for key in ("title", "target_file", "content", "portfolio_reason", "test_instructions", "change_kind"):
            if not task.get(key):
                raise ValueError(f"task {task_id} is missing {key}")
    return tasks


def task_marker(task_id: str) -> str:
    return MARKER_TEMPLATE.format(task_id=task_id)


def is_task_complete(root: Path, task: dict[str, str]) -> bool:
    target = root / task["target_file"]
    return target.exists() and task_marker(task["id"]) in target.read_text(encoding="utf-8")


def select_next_task(tasks: list[dict[str, str]], root: Path) -> dict[str, str] | None:
    for task in tasks:
        if not is_task_complete(root, task):
            return task
    return None


def branch_name(task: dict[str, str]) -> str:
    return f"{BRANCH_PREFIX}{task['id']}"


def render_task_document(task: dict[str, str]) -> str:
    return "\n".join(
        [
            f"# {task['title']}",
            "",
            task_marker(task["id"]),
            "",
            task["content"].rstrip(),
            "",
            "## Portfolio Value",
            "",
            task["portfolio_reason"].rstrip(),
            "",
            "## Validation",
            "",
            task["test_instructions"].rstrip(),
            "",
        ]
    )


def pr_body(task: dict[str, str]) -> str:
    return "\n".join(
        [
            "This PR was generated from the daily portfolio backlog.",
            "",
            "## What changed",
            f"- Added `{task['target_file']}`",
            f"- Task: `{task['id']}`",
            "",
            "## Why it matters",
            task["portfolio_reason"],
            "",
            "## Test/check instructions",
            task["test_instructions"],
            "",
            "## Change type",
            task["change_kind"],
            "",
            "Guardrails: this workflow creates a PR only. It does not push directly to `main`.",
        ]
    )


def run(command: list[str], *, capture: bool = False, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        check=check,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
    )


def open_daily_pr_count(repo: str) -> int:
    result = run(
        [
            "gh",
            "pr",
            "list",
            "--repo",
            repo,
            "--state",
            "open",
            "--json",
            "headRefName",
            "--jq",
            f'[.[] | select(.headRefName | startswith("{BRANCH_PREFIX}"))] | length',
        ],
        capture=True,
    )
    return int(result.stdout.strip() or "0")


def remote_branch_exists(branch: str) -> bool:
    result = run(["git", "ls-remote", "--heads", "origin", branch], capture=True, check=False)
    return bool(result.stdout.strip())


def write_github_output(values: dict[str, str]) -> None:
    output_path = os.environ.get("GITHUB_OUTPUT")
    if not output_path:
        return
    with Path(output_path).open("a", encoding="utf-8") as output:
        for key, value in values.items():
            output.write(f"{key}={value}\n")


def apply_task(root: Path, task: dict[str, str]) -> Path:
    target = root / task["target_file"]
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_task_document(task), encoding="utf-8")
    return target


def create_pull_request(repo: str, base: str, branch: str, task: dict[str, str]) -> bool:
    result = run(
        [
            "gh",
            "pr",
            "create",
            "--repo",
            repo,
            "--base",
            base,
            "--head",
            branch,
            "--title",
            f"daily: {task['title']}",
            "--body",
            pr_body(task),
        ],
        capture=True,
        check=False,
    )
    if result.returncode == 0:
        print(result.stdout.strip())
        write_github_output({"created": "true", "task_id": task["id"], "branch": branch})
        return True

    details = "\n".join(part.strip() for part in (result.stdout, result.stderr) if part and part.strip())
    print("Unable to create the pull request. The branch was left available for retry.")
    if details:
        print(details)
    write_github_output({"created": "false", "reason": "pr-create-failed", "task_id": task["id"], "branch": branch})
    return False


def create_pr(root: Path, task: dict[str, str], repo: str, base: str) -> None:
    branch = branch_name(task)
    if remote_branch_exists(branch):
        print(f"Remote branch {branch} already exists; creating PR from the existing branch.")
        run(["git", "fetch", "origin", branch])
        run(["git", "checkout", "-B", branch, f"origin/{branch}"])
        create_pull_request(repo, base, branch, task)
        return

    run(["git", "checkout", "-B", branch])
    target = apply_task(root, task)
    status = run(["git", "status", "--porcelain"], capture=True)
    if not status.stdout.strip():
        write_github_output({"created": "false", "reason": "empty-diff"})
        print("No changes generated; skipping PR.")
        return
    run(["git", "add", str(target.relative_to(root))])
    run(["git", "commit", "-m", f"daily: {task['title']}"])
    run(["git", "push", "--set-upstream", "origin", branch])
    create_pull_request(repo, base, branch, task)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create one deterministic daily portfolio PR.")
    parser.add_argument("--backlog", default=".github/daily-pr/backlog.json")
    parser.add_argument("--repo", default=os.environ.get("DAILY_PR_REPO", ""))
    parser.add_argument("--base", default="main")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--create-pr", action="store_true")
    args = parser.parse_args(argv)

    root = Path.cwd()
    tasks = load_tasks(root / args.backlog)
    task = select_next_task(tasks, root)
    if task is None:
        write_github_output({"created": "false", "reason": "backlog-complete"})
        print("Backlog is complete; nothing to do.")
        return 0

    print(f"Selected task: {task['id']} - {task['title']}")
    if args.dry_run:
        print(f"Would create {branch_name(task)} and {task['target_file']}")
        return 0

    if args.create_pr:
        if not args.repo:
            raise ValueError("--repo or DAILY_PR_REPO is required when creating a PR")
        if open_daily_pr_count(args.repo) > 0:
            write_github_output({"created": "false", "reason": "open-daily-pr-exists"})
            print("An open daily PR already exists; skipping.")
            return 0
        create_pr(root, task, args.repo, args.base)
        return 0

    apply_task(root, task)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
