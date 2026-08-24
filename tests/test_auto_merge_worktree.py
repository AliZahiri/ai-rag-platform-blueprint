import os
import shlex
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / ".github/scripts/auto_merge_daily_prs.sh"


class AutoMergeWorktreeTests(unittest.TestCase):
    def git(self, cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", *args],
            cwd=cwd,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def test_pr_tests_run_in_temporary_worktree_without_moving_base_checkout(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            remote = root / "remote.git"
            seed = root / "seed"
            runner = root / "runner"
            self.git(root, "init", "--bare", str(remote))
            self.git(root, "init", "--initial-branch=main", str(seed))
            self.git(seed, "config", "user.name", "Test User")
            self.git(seed, "config", "user.email", "test@example.invalid")
            (seed / "tests").mkdir()
            (seed / "tests/test_smoke.py").write_text(
                "import unittest\n\nclass SmokeTests(unittest.TestCase):\n"
                "    def test_passes(self):\n        self.assertTrue(True)\n",
                encoding="utf-8",
            )
            self.git(seed, "add", "tests/test_smoke.py")
            self.git(seed, "commit", "-m", "test: add smoke test")
            self.git(seed, "remote", "add", "origin", str(remote))
            self.git(seed, "push", "-u", "origin", "main")
            self.git(seed, "switch", "-c", "daily/sample")
            (seed / "feature.py").write_text("ENABLED = True\n", encoding="utf-8")
            self.git(seed, "add", "feature.py")
            self.git(seed, "commit", "-m", "feat: add sample")
            self.git(seed, "push", "-u", "origin", "daily/sample")
            self.git(root, "clone", "--branch", "main", str(remote), str(runner))

            before_head = self.git(runner, "rev-parse", "HEAD").stdout.strip()
            env = {
                **os.environ,
                "GITHUB_REPOSITORY": "example/example",
                "REQUIRED_CHECK_NAMES": "python",
            }
            command = f"source {shlex.quote(str(SCRIPT_PATH))}; run_pr_tests daily/sample"
            result = subprocess.run(
                ["bash", "-c", command],
                cwd=runner,
                env=env,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(self.git(runner, "rev-parse", "HEAD").stdout.strip(), before_head)
            self.assertEqual(self.git(runner, "branch", "--show-current").stdout.strip(), "main")
            self.assertEqual(self.git(runner, "status", "--porcelain").stdout, "")
            worktrees = self.git(runner, "worktree", "list", "--porcelain").stdout
            self.assertEqual(worktrees.count("worktree "), 1)


if __name__ == "__main__":
    unittest.main()
