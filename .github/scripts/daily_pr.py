from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from pathlib import Path, PurePosixPath


MARKER_TEMPLATE = "<!-- daily-pr-task: {task_id} -->"
BRANCH_PREFIX = "daily/"
ISSUE_LABEL = "daily-portfolio"


def load_tasks(backlog_path: Path) -> list[dict[str, str]]:
    data = json.loads(backlog_path.read_text(encoding="utf-8"))
    tasks = data["tasks"] if isinstance(data, dict) else data
    for task in tasks:
        task_id = task.get("id", "")
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", task_id):
            raise ValueError(f"invalid task id: {task_id}")
        for key in ("title", "portfolio_reason", "test_instructions", "change_kind"):
            if not task.get(key):
                raise ValueError(f"task {task_id} is missing {key}")
        task_files(task)
    return tasks


def validate_relative_path(value: str) -> str:
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"invalid task file path: {value}")
    return value


def task_files(task: dict[str, object]) -> list[dict[str, str]]:
    files = task.get("files")
    if files is not None:
        if not isinstance(files, list) or not files:
            raise ValueError(f"task {task.get('id', '')} files must be a non-empty list")
        normalized = []
        for item in files:
            if not isinstance(item, dict):
                raise ValueError(f"task {task.get('id', '')} file entries must be objects")
            path = str(item.get("path", ""))
            content = str(item.get("content", ""))
            if not path or not content:
                raise ValueError(f"task {task.get('id', '')} file entries need path and content")
            normalized.append(
                {
                    "path": validate_relative_path(path),
                    "content": content,
                    "kind": str(item.get("kind", "raw")),
                }
            )
        return normalized

    target_file = str(task.get("target_file", ""))
    content = str(task.get("content", ""))
    if not target_file or not content:
        raise ValueError(f"task {task.get('id', '')} is missing target_file/content or files")
    return [{"path": validate_relative_path(target_file), "content": content, "kind": "document"}]


def task_marker(task_id: str) -> str:
    return MARKER_TEMPLATE.format(task_id=task_id)


def is_task_complete(root: Path, task: dict[str, str]) -> bool:
    targets = [root / item["path"] for item in task_files(task)]
    if not all(target.exists() for target in targets):
        return False
    marker = task_marker(task["id"])
    return any(marker in target.read_text(encoding="utf-8") for target in targets)


def select_next_task(tasks: list[dict[str, str]], root: Path) -> dict[str, str] | None:
    for task in tasks:
        if not is_task_complete(root, task):
            return task
    return None


def branch_name(task: dict[str, str]) -> str:
    return f"{BRANCH_PREFIX}{task['id']}"


def task_for_branch(tasks: list[dict[str, str]], branch: str) -> dict[str, str] | None:
    if not branch.startswith(BRANCH_PREFIX):
        return None
    task_id = branch.removeprefix(BRANCH_PREFIX)
    return next((task for task in tasks if task["id"] == task_id), None)


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


def render_task_file(task: dict[str, str], item: dict[str, str]) -> str:
    if item.get("kind") == "document":
        return render_task_document({**task, "content": item["content"]})
    return item["content"].rstrip() + "\n"


def task_file_paths(task: dict[str, object]) -> list[str]:
    return [item["path"] for item in task_files(task)]


def issue_title(task: dict[str, str]) -> str:
    return f"daily: {task['title']}"


def issue_body(task: dict[str, str]) -> str:
    return "\n".join(
        [
            "This issue tracks one item from the daily portfolio automation backlog.",
            "",
            task_marker(task["id"]),
            "",
            "## Task",
            task["title"],
            "",
            "## Why it matters",
            task["portfolio_reason"],
            "",
            "## Acceptance checks",
            task["test_instructions"],
            "",
            "## Change type",
            task["change_kind"],
        ]
    )


def issue_reference(issue: dict[str, object]) -> str:
    number = issue.get("number")
    if number:
        return f"#{number}"
    return str(issue.get("url", "")).strip()


def pr_body(task: dict[str, str], issue: dict[str, object] | None = None) -> str:
    issue_section: list[str] = []
    if issue:
        issue_section = [
            "## Linked issue",
            f"Closes {issue_reference(issue)}",
            "",
        ]

    return "\n".join(
        [
            "This PR was generated from the daily portfolio backlog.",
            "",
            *issue_section,
            "## What changed",
            *[f"- Added or updated `{path}`" for path in task_file_paths(task)],
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
    return len(open_daily_prs(repo))


def open_daily_prs(repo: str) -> list[dict[str, object]]:
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
            "number,title,headRefName,body,url",
            "--jq",
            f'[.[] | select(.headRefName | startswith("{BRANCH_PREFIX}"))]',
        ],
        capture=True,
    )
    return json.loads(result.stdout or "[]")


def ensure_issue_label(repo: str) -> None:
    result = run(
        [
            "gh",
            "label",
            "create",
            ISSUE_LABEL,
            "--repo",
            repo,
            "--color",
            "1f6feb",
            "--description",
            "Daily portfolio automation backlog",
            "--force",
        ],
        capture=True,
        check=False,
    )
    if result.returncode != 0:
        details = "\n".join(part.strip() for part in (result.stdout, result.stderr) if part and part.strip())
        print("Unable to create or update the daily portfolio label.")
        if details:
            print(details)


def find_existing_issue(repo: str, task: dict[str, str]) -> dict[str, object] | None:
    result = run(
        [
            "gh",
            "issue",
            "list",
            "--repo",
            repo,
            "--state",
            "open",
            "--limit",
            "100",
            "--json",
            "number,title,body,url",
        ],
        capture=True,
    )
    marker = task_marker(task["id"])
    for issue in json.loads(result.stdout or "[]"):
        if issue.get("title") == issue_title(task) or marker in str(issue.get("body", "")):
            return issue
    return None


def create_issue(repo: str, task: dict[str, str]) -> dict[str, object]:
    ensure_issue_label(repo)
    result = run(
        [
            "gh",
            "issue",
            "create",
            "--repo",
            repo,
            "--title",
            issue_title(task),
            "--body",
            issue_body(task),
            "--label",
            ISSUE_LABEL,
        ],
        capture=True,
        check=False,
    )
    if result.returncode != 0:
        details = "\n".join(part.strip() for part in (result.stdout, result.stderr) if part and part.strip())
        raise RuntimeError(f"Unable to create issue for {task['id']}:\n{details}")

    url = result.stdout.strip().splitlines()[-1]
    number_text = url.rstrip("/").split("/")[-1]
    issue: dict[str, object] = {"title": issue_title(task), "url": url}
    if number_text.isdigit():
        issue["number"] = int(number_text)
    write_github_output({"issue_url": url, "issue_number": str(issue.get("number", ""))})
    print(f"Created issue {issue_reference(issue)} for task {task['id']}")
    return issue


def ensure_issue(repo: str, task: dict[str, str]) -> dict[str, object]:
    existing = find_existing_issue(repo, task)
    if existing:
        print(f"Using existing issue {issue_reference(existing)} for task {task['id']}")
        return existing
    return create_issue(repo, task)


def link_issue_to_open_pr(repo: str, pr: dict[str, object], issue: dict[str, object]) -> None:
    reference = issue_reference(issue)
    if not reference:
        return
    current_body = str(pr.get("body") or "")
    if reference in current_body:
        return

    updated_body = current_body.rstrip()
    if updated_body:
        updated_body += "\n\n"
    updated_body += f"## Linked issue\n\nCloses {reference}\n"
    result = run(
        [
            "gh",
            "pr",
            "edit",
            str(pr["number"]),
            "--repo",
            repo,
            "--body",
            updated_body,
        ],
        capture=True,
        check=False,
    )
    if result.returncode != 0:
        details = "\n".join(part.strip() for part in (result.stdout, result.stderr) if part and part.strip())
        raise RuntimeError(f"Unable to link issue to PR #{pr['number']}:\n{details}")
    print(f"Linked issue {reference} to open PR #{pr['number']}")


def update_open_pr_branch(root: Path, pr: dict[str, object], task: dict[str, str]) -> None:
    branch = str(pr.get("headRefName", ""))
    if not branch.startswith(BRANCH_PREFIX):
        return
    print(f"Syncing generated files into open PR branch {branch}")
    run(["git", "fetch", "origin", branch])
    run(["git", "checkout", "-B", branch, f"origin/{branch}"])
    targets = apply_task(root, task)
    status = run(["git", "status", "--porcelain"], capture=True)
    if not status.stdout.strip():
        print(f"Open PR branch {branch} already has the current generated files.")
        return
    run(["git", "add", *[str(target.relative_to(root)) for target in targets]])
    run(["git", "commit", "-m", f"daily: expand {task['title']}"])
    run(["git", "push", "origin", branch])


def sync_open_pr_issues(root: Path, repo: str, prs: list[dict[str, object]], tasks: list[dict[str, str]]) -> None:
    for pr in prs:
        task = task_for_branch(tasks, str(pr.get("headRefName", "")))
        if not task:
            print(f"Open daily PR #{pr.get('number')} does not match a backlog task; skipping issue sync.")
            continue
        update_open_pr_branch(root, pr, task)
        issue = ensure_issue(repo, task)
        link_issue_to_open_pr(repo, pr, issue)


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


def apply_task(root: Path, task: dict[str, str]) -> list[Path]:
    targets = []
    for item in task_files(task):
        target = root / item["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render_task_file(task, item), encoding="utf-8")
        targets.append(target)
    return targets


def create_pull_request(
    repo: str,
    base: str,
    branch: str,
    task: dict[str, str],
    issue: dict[str, object] | None = None,
) -> bool:
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
            pr_body(task, issue),
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
        targets = apply_task(root, task)
        status = run(["git", "status", "--porcelain"], capture=True)
        if status.stdout.strip():
            run(["git", "add", *[str(target.relative_to(root)) for target in targets]])
            run(["git", "commit", "-m", f"daily: expand {task['title']}"])
            run(["git", "push", "origin", branch])
        issue = ensure_issue(repo, task)
        create_pull_request(repo, base, branch, task, issue)
        return

    run(["git", "checkout", "-B", branch])
    targets = apply_task(root, task)
    status = run(["git", "status", "--porcelain"], capture=True)
    if not status.stdout.strip():
        write_github_output({"created": "false", "reason": "empty-diff"})
        print("No changes generated; skipping PR.")
        return
    run(["git", "add", *[str(target.relative_to(root)) for target in targets]])
    run(["git", "commit", "-m", f"daily: {task['title']}"])
    run(["git", "push", "--set-upstream", "origin", branch])
    issue = ensure_issue(repo, task)
    create_pull_request(repo, base, branch, task, issue)


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
        print(f"Would create {branch_name(task)} and {', '.join(task_file_paths(task))}")
        return 0

    if args.create_pr:
        if not args.repo:
            raise ValueError("--repo or DAILY_PR_REPO is required when creating a PR")
        open_prs = open_daily_prs(args.repo)
        if open_prs:
            sync_open_pr_issues(root, args.repo, open_prs, tasks)
            write_github_output({"created": "false", "reason": "open-daily-pr-exists"})
            print("An open daily PR already exists; skipping.")
            return 0
        create_pr(root, task, args.repo, args.base)
        return 0

    apply_task(root, task)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
