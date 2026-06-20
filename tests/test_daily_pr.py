import importlib.util
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
    def test_branch_name_uses_daily_prefix(self):
        self.assertEqual(daily_pr.branch_name({"id": "benchmark-plan"}), "daily/benchmark-plan")

    def test_task_for_branch_matches_backlog_id(self):
        task = sample_task()

        selected = daily_pr.task_for_branch([task], "daily/sample")

        self.assertEqual(selected["id"], "sample")

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
            first = {"id": "done", "target_file": "docs/done.md"}
            second = {"id": "next", "target_file": "docs/next.md"}
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
