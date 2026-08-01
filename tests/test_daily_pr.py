import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / ".github/scripts/daily_pr.py"
SPEC = importlib.util.spec_from_file_location("daily_pr", SCRIPT_PATH)
daily_pr = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(daily_pr)


def sample_task():
    return {
        "id": "sample",
        "title": "Sample Task",
        "target_file": "docs/sample.md",
        "content": "Content",
        "portfolio_reason": "Reason",
        "test_instructions": "Checks",
        "change_kind": "docs-only",
    }


class DailyPrTests(unittest.TestCase):
    def write_backlog(self, root, tasks):
        backlog = Path(root) / "backlog.json"
        backlog.write_text(json.dumps({"tasks": tasks}), encoding="utf-8")
        return backlog

    def test_branch_name_uses_daily_prefix(self):
        self.assertEqual(daily_pr.branch_name({"id": "benchmark-plan"}), "daily/benchmark-plan")

    def test_task_for_branch_matches_backlog_id(self):
        task = sample_task()

        selected = daily_pr.task_for_branch([task], "daily/sample")

        self.assertEqual(selected["id"], "sample")

    def test_task_files_support_multiple_generated_files(self):
        task = {
            **sample_task(),
            "files": [
                {"path": "docs/sample.md", "kind": "document", "content": "Docs"},
                {"path": "tests/test_sample.py", "content": "print('ok')"},
            ],
        }

        files = daily_pr.task_files(task)

        self.assertEqual([item["path"] for item in files], ["docs/sample.md", "tests/test_sample.py"])

    def test_task_files_reject_parent_directory_paths(self):
        task = {**sample_task(), "files": [{"path": "../bad.py", "content": "bad"}]}

        with self.assertRaises(ValueError):
            daily_pr.task_files(task)

    def test_load_tasks_rejects_duplicate_task_ids(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tasks = [sample_task(), {**sample_task(), "target_file": "docs/other.md"}]

            with self.assertRaisesRegex(ValueError, "duplicate task id: sample"):
                daily_pr.load_tasks(self.write_backlog(tmpdir, tasks))

    def test_load_tasks_rejects_duplicate_target_paths(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tasks = [sample_task(), {**sample_task(), "id": "other"}]

            with self.assertRaisesRegex(ValueError, "duplicate incomplete task file path: docs/sample.md"):
                daily_pr.load_tasks(self.write_backlog(tmpdir, tasks))

    def test_load_tasks_allows_completed_task_path_to_be_evolved(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            target = root / "docs/sample.md"
            target.parent.mkdir(parents=True)
            target.write_text(daily_pr.task_marker("sample"), encoding="utf-8")
            tasks = [sample_task(), {**sample_task(), "id": "follow-up"}]

            loaded = daily_pr.load_tasks(self.write_backlog(tmpdir, tasks))

            self.assertEqual(["sample", "follow-up"], [task["id"] for task in loaded])

    def test_load_tasks_compile_checks_python_without_executing_it(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            task = {
                **sample_task(),
                "files": [
                    {
                        "path": "scripts/broken.py",
                        "content": "raise RuntimeError('must not execute')\ndef broken(:\n",
                    }
                ],
            }

            with self.assertRaisesRegex(ValueError, "task sample has invalid Python in scripts/broken.py"):
                daily_pr.load_tasks(self.write_backlog(tmpdir, [task]))

    def test_issue_body_includes_task_marker(self):
        rendered = daily_pr.issue_body(sample_task())

        self.assertIn("<!-- daily-pr-task: sample -->", rendered)
        self.assertIn("## Acceptance checks", rendered)

    def test_pr_body_links_issue_when_available(self):
        rendered = daily_pr.pr_body(sample_task(), {"number": 42, "url": "https://example.test/issues/42"})

        self.assertIn("## Linked issue", rendered)
        self.assertIn("Closes #42", rendered)

    def test_select_next_task_skips_completed_task(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            first = {"id": "done", "target_file": "docs/done.md", "content": "Done"}
            second = {"id": "next", "target_file": "docs/next.md", "content": "Next"}
            target = root / first["target_file"]
            target.parent.mkdir(parents=True)
            target.write_text(daily_pr.task_marker("done"), encoding="utf-8")

            selected = daily_pr.select_next_task([first, second], root)

            self.assertEqual(selected["id"], "next")

    def test_render_task_document_includes_marker_and_validation(self):
        task = sample_task()

        rendered = daily_pr.render_task_document(task)

        self.assertIn("<!-- daily-pr-task: sample -->", rendered)
        self.assertIn("## Validation", rendered)


if __name__ == "__main__":
    unittest.main()
