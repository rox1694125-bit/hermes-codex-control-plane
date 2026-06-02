#!/usr/bin/env python3
"""Regression tests for the Hermes-Codex control-plane doctor."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOCTOR = REPO_ROOT / "scripts" / "check_control_plane.py"
FIXTURES = REPO_ROOT / "tests" / "fixtures"


def run_doctor(project: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(DOCTOR), str(project), *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def parse_json(result: subprocess.CompletedProcess[str]) -> dict:
    return json.loads(result.stdout)


def assert_report_shape(test_case: unittest.TestCase, report: dict) -> None:
    test_case.assertEqual(set(report), {"ok", "project_path", "errors", "warnings", "summary"})
    for collection_name in ("errors", "warnings"):
        for finding in report[collection_name]:
            test_case.assertEqual(set(finding), {"code", "message", "path"})


class ControlPlaneDoctorTests(unittest.TestCase):
    def test_pass_project_has_no_errors_or_warnings(self) -> None:
        result = run_doctor(FIXTURES / "pass-project", "--json")
        report = parse_json(result)

        assert_report_shape(self, report)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(report["ok"])
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["warnings"], [])
        self.assertEqual(report["summary"], {"errors": 0, "warnings": 0})
        self.assertIn("project_path", report)

    def test_strict_warnings_clean_project_returns_zero(self) -> None:
        result = run_doctor(FIXTURES / "pass-project", "--strict-warnings", "--json")
        report = parse_json(result)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(report["ok"])
        self.assertEqual(report["warnings"], [])

    def test_warning_project_does_not_fail(self) -> None:
        result = run_doctor(FIXTURES / "warn-template-project", "--json")
        report = parse_json(result)
        warning_codes = {item["code"] for item in report["warnings"]}

        assert_report_shape(self, report)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(report["ok"])
        self.assertEqual(report["errors"], [])
        self.assertIn("placeholder", warning_codes)
        self.assertGreater(report["summary"]["warnings"], 0)

    def test_optional_docs_are_not_required(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir) / "project"
            shutil.copytree(FIXTURES / "pass-project", project)
            (project / "docs" / "SOURCE_POLICY.md").unlink()
            (project / "docs" / "TERMS.md").unlink()

            result = run_doctor(project, "--json")

        report = parse_json(result)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(report["ok"])
        self.assertEqual(report["warnings"], [])

    def test_warning_project_reports_warn_status_in_human_output(self) -> None:
        result = run_doctor(FIXTURES / "warn-template-project")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Hermes-Codex Control Plane Doctor: WARN", result.stdout)
        self.assertIn("Warnings", result.stdout)

    def test_strict_warnings_returns_exit_one(self) -> None:
        result = run_doctor(FIXTURES / "warn-template-project", "--strict-warnings", "--json")
        report = parse_json(result)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertTrue(report["ok"])
        self.assertGreater(report["summary"]["warnings"], 0)

    def test_missing_required_file_fails_with_exit_one(self) -> None:
        result = run_doctor(FIXTURES / "fail-missing-workplan", "--json")
        report = parse_json(result)
        errors = {(item["code"], item["path"]) for item in report["errors"]}

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertFalse(report["ok"])
        self.assertIn(("missing_required_file", "WORKPLAN.md"), errors)

    def test_errors_take_precedence_over_warnings_in_human_output(self) -> None:
        result = run_doctor(FIXTURES / "fail-missing-workplan")

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("Hermes-Codex Control Plane Doctor: FAIL", result.stdout)

    def test_safety_scan_catches_generated_private_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir) / "unsafe-project"
            shutil.copytree(FIXTURES / "pass-project", project)
            (project / ".env").write_text("TOKEN=do-not-commit\n", encoding="utf-8")
            (project / "secrets").mkdir()
            private_path = "/".join(("", "Users", "alice", "hermes", "private"))
            fake_token = "ghp_" + "1234567890abcdef" + "1234567890abcdef" + "1234"
            (project / "docs" / "private-notes.md").write_text(
                f"Local path: {private_path}\n"
                f"Token: {fake_token}\n",
                encoding="utf-8",
            )

            result = run_doctor(project, "--json")

        report = parse_json(result)
        error_codes = {item["code"] for item in report["errors"]}

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertFalse(report["ok"])
        self.assertIn("secret_file", error_codes)
        self.assertIn("secret_dir", error_codes)
        self.assertIn("private_path", error_codes)
        self.assertIn("token_like_secret", error_codes)

    def test_missing_project_is_usage_error(self) -> None:
        missing = Path(tempfile.gettempdir()) / "control-plane-doctor-missing-project"
        result = run_doctor(missing, "--json")
        report = parse_json(result)

        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertFalse(report["ok"])
        self.assertEqual(report["errors"][0]["code"], "missing_project")

    def test_file_path_is_usage_error(self) -> None:
        target_file = FIXTURES / "pass-project" / "AGENTS.md"
        result = run_doctor(target_file, "--json")
        report = parse_json(result)

        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertFalse(report["ok"])
        self.assertEqual(report["errors"][0]["code"], "not_a_directory")

    def test_human_output_reports_pass_status(self) -> None:
        result = run_doctor(FIXTURES / "pass-project")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Hermes-Codex Control Plane Doctor: PASS", result.stdout)
        self.assertIn("Errors: 0  Warnings: 0", result.stdout)


if __name__ == "__main__":
    unittest.main()
