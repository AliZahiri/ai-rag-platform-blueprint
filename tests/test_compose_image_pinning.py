from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import tempfile
import unittest

from scripts.compose_image_pinning import (
    compose_image_pinning_violations,
    main,
    validate_files,
)


ROOT = Path(__file__).resolve().parents[1]
COMPOSE_PATH = ROOT / "compose" / "docker-compose.yml"
ENVIRONMENT_PATH = ROOT / "env" / ".env.example"
PINNED_POSTGRES = "postgres@sha256:" + "a" * 64


class ComposeImagePinningTests(unittest.TestCase):
    def test_project_defaults_and_environment_overrides_are_pinned(self):
        self.assertEqual((), validate_files(COMPOSE_PATH, ENVIRONMENT_PATH))

    def test_mutable_missing_mismatched_and_nonstandard_images_are_rejected(self):
        cases = (
            (
                "services:\n  db:\n    image: ${POSTGRES_IMAGE:-postgres:latest}\n",
                {"POSTGRES_IMAGE": PINNED_POSTGRES},
                "line_3:default_image_is_not_digest_pinned",
            ),
            (
                "services:\n  db:\n    image: ${POSTGRES_IMAGE:-" + PINNED_POSTGRES + "}\n",
                {},
                "POSTGRES_IMAGE:environment_override_is_missing",
            ),
            (
                "services:\n  db:\n    image: ${POSTGRES_IMAGE:-" + PINNED_POSTGRES + "}\n",
                {"POSTGRES_IMAGE": "postgres:16-alpine"},
                "POSTGRES_IMAGE:environment_image_is_not_digest_pinned",
            ),
            (
                "services:\n  db:\n    image: postgres:16-alpine\n",
                {"POSTGRES_IMAGE": PINNED_POSTGRES},
                "line_3:image_must_use_a_variable_with_a_digest_default",
            ),
        )
        for compose, environment, expected in cases:
            with self.subTest(expected=expected):
                self.assertIn(expected, compose_image_pinning_violations(compose, environment))

    def test_environment_drift_and_duplicates_are_rejected(self):
        compose = "services:\n  db:\n    image: ${POSTGRES_IMAGE:-" + PINNED_POSTGRES + "}\n"
        mismatched = "postgres@sha256:" + "b" * 64
        self.assertIn(
            "POSTGRES_IMAGE:environment_image_does_not_match_compose_default",
            compose_image_pinning_violations(compose, {"POSTGRES_IMAGE": mismatched}),
        )
        with tempfile.TemporaryDirectory() as directory:
            environment_path = Path(directory) / "example.env"
            environment_path.write_text("POSTGRES_IMAGE=x\nPOSTGRES_IMAGE=y\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicated"):
                validate_files(COMPOSE_PATH, environment_path)

    def test_json_cli_preserves_policy_and_execution_exit_codes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            compose = root / "compose.yml"
            environment = root / "example.env"
            compose.write_text(
                "services:\n  db:\n    image: ${POSTGRES_IMAGE:-" + PINNED_POSTGRES + "}\n",
                encoding="utf-8",
            )
            environment.write_text("POSTGRES_IMAGE=" + PINNED_POSTGRES + "\n", encoding="utf-8")
            output = StringIO()
            with redirect_stdout(output):
                self.assertEqual(0, main(["--compose", str(compose), "--env", str(environment), "--json"]))
            self.assertIn('"status": "passed"', output.getvalue())

            environment.write_text("POSTGRES_IMAGE=postgres:latest\n", encoding="utf-8")
            with redirect_stdout(StringIO()):
                self.assertEqual(1, main(["--compose", str(compose), "--env", str(environment), "--json"]))
            with redirect_stdout(StringIO()):
                self.assertEqual(2, main(["--compose", str(root / "missing.yml"), "--env", str(environment), "--json"]))


if __name__ == "__main__":
    unittest.main()
