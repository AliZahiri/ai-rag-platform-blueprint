import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / ".github/scripts/daily_pr.py"
SPEC = importlib.util.spec_from_file_location("daily_pr", SCRIPT_PATH)
daily_pr = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(daily_pr)


class DailyPrTests(unittest.TestCase):
    def test_branch_name_uses_daily_prefix(self):
        self.assertEqual(daily_pr.branch_name({"id": "benchmark-plan"}), "daily/benchmark-plan")

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
        task = {
            "id": "sample",
            "title": "Sample Task",
            "content": "Content",
            "portfolio_reason": "Reason",
            "test_instructions": "Checks",
            "change_kind": "docs-only",
        }

        rendered = daily_pr.render_task_document(task)

        self.assertIn("<!-- daily-pr-task: sample -->", rendered)
        self.assertIn("## Validation", rendered)


if __name__ == "__main__":
    unittest.main()
