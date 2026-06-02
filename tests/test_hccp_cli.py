#!/usr/bin/env python3
"""Regression tests for the unified hccp CLI."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
HCCP = REPO_ROOT / "scripts" / "hccp.py"


def run_hccp(*args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(HCCP), *args],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


class HccpCliTests(unittest.TestCase):
    def temp_codex_env(self, codex_home: Path) -> dict[str, str]:
        env = os.environ.copy()
        env["CODEX_HOME"] = str(codex_home)
        return env

    def test_help_succeeds(self) -> None:
        result = run_hccp("--help")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Unified CLI", result.stdout)
        self.assertIn("doctor", result.stdout)

    def test_doctor_wraps_control_plane_doctor(self) -> None:
        result = run_hccp("doctor", "examples/knowledge-ingestion-agent")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Hermes-Codex Control Plane Doctor: PASS", result.stdout)

    def test_repo_doctor_wraps_repo_linter(self) -> None:
        result = run_hccp("repo-doctor", "--strict-warnings")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Hermes-Codex Repo Linter: PASS", result.stdout)

    def test_demo_wraps_runnable_demo(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "demo-output"
            result = run_hccp("demo", "--output", str(output_dir), "--json")

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            summary = json.loads(result.stdout)
            self.assertTrue(summary["ok"])
            self.assertTrue((output_dir / "index.json").is_file())

    def test_demo_forwards_missing_input_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            missing = Path(temp_dir) / "missing.txt"
            result = run_hccp("demo", "--input", str(missing))

            self.assertEqual(result.returncode, 2)
            self.assertIn("Input file does not exist", result.stderr)

    def test_demo_forwards_empty_input_error(self) -> None:
        result = run_hccp("demo", "--input", "")

        self.assertEqual(result.returncode, 2)
        self.assertIn("Input file does not exist", result.stderr)

    def test_init_wraps_project_initializer(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir) / "project"
            project.mkdir()
            result = run_hccp("init", str(project))

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((project / "AGENTS.md").is_file())
            self.assertTrue((project / "docs" / "project-log").is_dir())

    def test_skill_status_reports_missing_skills(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            codex_home = Path(temp_dir) / "codex-home"
            result = run_hccp("skill-status", "--json", env=self.temp_codex_env(codex_home))

            report = json.loads(result.stdout)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertFalse(report["ok"])
            self.assertEqual(report["summary"]["missing"], 2)
            self.assertFalse((codex_home / "skills").exists())

    def test_install_skills_check_reports_missing_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            codex_home = Path(temp_dir) / "codex-home"
            result = run_hccp("install-skills", "--check", "--json", env=self.temp_codex_env(codex_home))

            report = json.loads(result.stdout)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertFalse(report["ok"])
            self.assertEqual(report["summary"]["missing"], 2)
            self.assertFalse((codex_home / "skills").exists())

    def test_install_skills_then_status_reports_current(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            codex_home = Path(temp_dir) / "codex-home"
            env = self.temp_codex_env(codex_home)

            install = run_hccp("install-skills", env=env)
            status = run_hccp("skill-status", "--json", env=env)

            report = json.loads(status.stdout)
            self.assertEqual(install.returncode, 0, install.stdout + install.stderr)
            self.assertEqual(status.returncode, 0, status.stdout + status.stderr)
            self.assertTrue(report["ok"])
            self.assertEqual(report["summary"]["current"], 2)
            self.assertEqual(report["errors"], [])

    def test_skill_status_detects_outdated_installed_skill(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            codex_home = Path(temp_dir) / "codex-home"
            env = self.temp_codex_env(codex_home)

            install = run_hccp("install-skills", env=env)
            skill_file = codex_home / "skills" / "hermes-architecture" / "SKILL.md"
            content = skill_file.read_text(encoding="utf-8")
            skill_file.write_text(content.replace("version: 0.6", "version: 0.1", 1), encoding="utf-8")
            status = run_hccp("skill-status", "--json", env=env)

            report = json.loads(status.stdout)
            error_codes = {item["code"] for item in report["errors"]}
            skill_statuses = {item["name"]: item["status"] for item in report["skills"]}

            self.assertEqual(install.returncode, 0, install.stdout + install.stderr)
            self.assertEqual(status.returncode, 1, status.stdout + status.stderr)
            self.assertFalse(report["ok"])
            self.assertIn("installed_skill_mismatch", error_codes)
            self.assertEqual(skill_statuses["hermes-architecture"], "mismatch")


if __name__ == "__main__":
    unittest.main()
