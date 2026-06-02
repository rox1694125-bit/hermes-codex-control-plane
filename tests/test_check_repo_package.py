#!/usr/bin/env python3
"""Regression tests for the Hermes-Codex repository package linter."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
LINTER = REPO_ROOT / "scripts" / "check_repo_package.py"


def run_linter(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(LINTER), str(repo), *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def parse_json(result: subprocess.CompletedProcess[str]) -> dict:
    return json.loads(result.stdout)


def assert_report_shape(test_case: unittest.TestCase, report: dict) -> None:
    test_case.assertEqual(set(report), {"ok", "repo_path", "errors", "warnings", "summary"})
    for collection_name in ("errors", "warnings"):
        for finding in report[collection_name]:
            test_case.assertEqual(set(finding), {"code", "message", "path"})


class RepoPackageLinterTests(unittest.TestCase):
    def test_current_repo_passes(self) -> None:
        result = run_linter(REPO_ROOT, "--json")
        report = parse_json(result)

        assert_report_shape(self, report)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(report["ok"])
        self.assertEqual(report["errors"], [])

    def test_missing_required_file_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = Path(temp_dir) / "repo"
            shutil.copytree(REPO_ROOT, repo, ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"))
            (repo / "README.md").unlink()

            result = run_linter(repo, "--json")

        report = parse_json(result)
        errors = {(item["code"], item["path"]) for item in report["errors"]}

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertFalse(report["ok"])
        self.assertIn(("missing_repo_file", "README.md"), errors)

    def test_bad_skill_metadata_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = Path(temp_dir) / "repo"
            shutil.copytree(REPO_ROOT, repo, ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"))
            skill_file = repo / "skills" / "hermes-architecture" / "SKILL.md"
            content = skill_file.read_text(encoding="utf-8")
            skill_file.write_text(content.replace("name: hermes-architecture", "name: wrong-name", 1), encoding="utf-8")

            result = run_linter(repo, "--json")

        report = parse_json(result)
        error_codes = {item["code"] for item in report["errors"]}

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertFalse(report["ok"])
        self.assertIn("skill_name_mismatch", error_codes)

    def test_missing_template_referenced_by_init_script_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = Path(temp_dir) / "repo"
            shutil.copytree(REPO_ROOT, repo, ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"))
            (repo / "templates" / "project-standard" / "WORKPLAN.md").unlink()

            result = run_linter(repo, "--json")

        report = parse_json(result)
        error_codes = {item["code"] for item in report["errors"]}

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertFalse(report["ok"])
        self.assertIn("init_references_missing_template", error_codes)

    def test_safety_scan_catches_generated_private_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = Path(temp_dir) / "repo"
            shutil.copytree(REPO_ROOT, repo, ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"))
            (repo / ".env").write_text("TOKEN=do-not-commit\n", encoding="utf-8")
            (repo / "credentials").mkdir()
            private_path = "/".join(("", "Volumes", "private-disk", "hermes"))
            fake_token = "sk-" + "1234567890abcdef" + "1234567890abcdef"
            (repo / "docs" / "unsafe-note.md").write_text(
                f"Path: {private_path}\n"
                f"Token: {fake_token}\n",
                encoding="utf-8",
            )

            result = run_linter(repo, "--json")

        report = parse_json(result)
        error_codes = {item["code"] for item in report["errors"]}

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertFalse(report["ok"])
        self.assertIn("secret_file", error_codes)
        self.assertIn("secret_dir", error_codes)
        self.assertIn("private_path", error_codes)
        self.assertIn("token_like_secret", error_codes)

    def test_missing_repo_path_is_usage_error(self) -> None:
        missing = Path(tempfile.gettempdir()) / "hermes-codex-missing-repo"
        result = run_linter(missing, "--json")
        report = parse_json(result)

        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertFalse(report["ok"])
        self.assertEqual(report["errors"][0]["code"], "missing_repo")

    def test_file_path_is_usage_error(self) -> None:
        result = run_linter(REPO_ROOT / "README.md", "--json")
        report = parse_json(result)

        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertFalse(report["ok"])
        self.assertEqual(report["errors"][0]["code"], "not_a_directory")

    def test_human_output_reports_pass_status(self) -> None:
        result = run_linter(REPO_ROOT)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Hermes-Codex Repo Linter: PASS", result.stdout)


if __name__ == "__main__":
    unittest.main()
