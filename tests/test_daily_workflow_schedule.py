import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DAILY_WORKFLOW = ROOT / ".github" / "workflows" / "daily-pr.yml"


class DailyWorkflowScheduleTests(unittest.TestCase):
    def test_runs_once_daily_at_tehran_eight(self) -> None:
        content = DAILY_WORKFLOW.read_text(encoding="utf-8")

        self.assertEqual(1, content.count("cron:"))
        self.assertIn('cron: "30 4 * * *"', content)
        self.assertIn("08:00 Asia/Tehran", content)


if __name__ == "__main__":
    unittest.main()
