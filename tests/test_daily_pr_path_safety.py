import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / ".github/scripts/daily_pr.py"
SPEC = importlib.util.spec_from_file_location("daily_pr_paths", SCRIPT)
daily = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(daily)


def task(*paths):
    return {
        "id": "path-safety",
        "files": [{"path": path, "content": "generated"} for path in paths],
    }


class GeneratedPathSafetyTests(unittest.TestCase):
    def test_rejects_noncanonical_and_git_metadata_paths(self):
        for path in ("", ".", "./x.py", "a//b.py", "a/../b.py", "/tmp/x",
                     ".git/config", "nested/.GIT/config", "x/", "x\\y", "x\ny"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                daily.validate_relative_path(path)

    def test_duplicate_files_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate task file path"):
            daily.task_files(task("scripts/check.py", "scripts/check.py"))

    def test_regular_existing_file_can_be_updated(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "check.py"
            target.write_text("old")
            self.assertEqual([target], daily.apply_task(root, task("check.py")))
            self.assertEqual("generated\n", target.read_text())

    def test_external_directory_symlink_does_not_write_or_read(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "repo"
            outside = Path(directory) / "outside"
            root.mkdir()
            outside.mkdir()
            external = outside / "check.py"
            external.write_text(daily.task_marker("path-safety"))
            (root / "scripts").symlink_to(outside, target_is_directory=True)
            for operation in (daily.apply_task, daily.is_task_complete):
                with self.subTest(operation=operation.__name__):
                    with self.assertRaisesRegex(ValueError, "symlink"):
                        operation(root, task("scripts/check.py"))
            self.assertEqual(daily.task_marker("path-safety"), external.read_text())

    def test_internal_and_dangling_file_symlinks_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "real.py").write_text("old")
            for destination in ("real.py", "missing.py"):
                link = root / "link.py"
                link.symlink_to(destination)
                with self.subTest(destination=destination):
                    with self.assertRaisesRegex(ValueError, "symlink"):
                        daily.apply_task(root, task("link.py"))
                link.unlink()
            self.assertEqual("old", (root / "real.py").read_text())

    def test_all_paths_are_checked_before_first_write(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "unsafe").symlink_to("/tmp", target_is_directory=True)
            with self.assertRaises(ValueError):
                daily.apply_task(root, task("safe/check.py", "unsafe/check.py"))
            self.assertFalse((root / "safe").exists())

    def test_directory_target_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "scripts").mkdir()
            with self.assertRaisesRegex(ValueError, "regular file"):
                daily.apply_task(root, task("scripts"))

    def test_symlink_repository_root_is_supported(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            real = directory / "real"
            real.mkdir()
            alias = directory / "alias"
            alias.symlink_to(real, target_is_directory=True)
            daily.apply_task(alias, task("scripts/check.py"))
            self.assertEqual("generated\n", (real / "scripts/check.py").read_text())
