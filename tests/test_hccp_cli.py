#!/usr/bin/env python3
"""Regression tests for the unified hccp CLI."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
HCCP = REPO_ROOT / "scripts" / "hccp.py"


def run_hccp(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(HCCP), *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


class HccpCliTests(unittest.TestCase):
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

    def test_init_wraps_project_initializer(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir) / "project"
            project.mkdir()
            result = run_hccp("init", str(project))

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((project / "AGENTS.md").is_file())
            self.assertTrue((project / "docs" / "project-log").is_dir())


if __name__ == "__main__":
    unittest.main()
