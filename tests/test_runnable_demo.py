#!/usr/bin/env python3
"""Regression tests for the local runnable demo."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEMO = REPO_ROOT / "examples" / "knowledge-ingestion-agent" / "scripts" / "run_demo.py"
SAMPLE = REPO_ROOT / "examples" / "knowledge-ingestion-agent" / "fixtures" / "sample-article.txt"


def run_demo(output_dir: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(DEMO), "--input", str(SAMPLE), "--output", str(output_dir), *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


class RunnableDemoTests(unittest.TestCase):
    def test_demo_generates_expected_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "demo-output"
            result = run_demo(output_dir, "--json")

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            summary = json.loads(result.stdout)
            self.assertTrue(summary["ok"])

            index_path = output_dir / "index.json"
            report_path = output_dir / "reports" / "latest-run.json"
            note_path = output_dir / "notes" / "local-knowledge-ingestion-smoke-test.md"
            raw_files = list((output_dir / "raw").glob("*.txt"))

            self.assertTrue(index_path.is_file())
            self.assertTrue(report_path.is_file())
            self.assertTrue(note_path.is_file())
            self.assertEqual(len(raw_files), 1)

            index = json.loads(index_path.read_text(encoding="utf-8"))
            report = json.loads(report_path.read_text(encoding="utf-8"))
            record = index["records"][0]
            self.assertEqual(record["title"], "Local Knowledge Ingestion Smoke Test")
            self.assertGreater(record["word_count"], 50)
            self.assertIn("keywords", record)
            self.assertIn("summary", record)
            self.assertIn("Runtime Boundary", note_path.read_text(encoding="utf-8"))
            self.assertEqual(report["input"], "sample-article.txt")
            self.assertNotIn(str(REPO_ROOT), report_path.read_text(encoding="utf-8"))

    def test_demo_output_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_a = Path(temp_dir) / "a"
            output_b = Path(temp_dir) / "b"

            result_a = run_demo(output_a, "--json")
            result_b = run_demo(output_b, "--json")

            self.assertEqual(result_a.returncode, 0, result_a.stdout + result_a.stderr)
            self.assertEqual(result_b.returncode, 0, result_b.stdout + result_b.stderr)
            self.assertEqual(
                (output_a / "index.json").read_text(encoding="utf-8"),
                (output_b / "index.json").read_text(encoding="utf-8"),
            )

    def test_missing_input_returns_usage_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            missing = Path(temp_dir) / "missing.txt"
            output_dir = Path(temp_dir) / "out"
            result = subprocess.run(
                [sys.executable, str(DEMO), "--input", str(missing), "--output", str(output_dir)],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

        self.assertEqual(result.returncode, 2)
        self.assertIn("Input file does not exist", result.stderr)

    def test_url_input_is_rejected_without_fetching(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "out"
            result = subprocess.run(
                [
                    sys.executable,
                    str(DEMO),
                    "--input",
                    "https://example.com/article",
                    "--output",
                    str(output_dir),
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

        self.assertEqual(result.returncode, 2)
        self.assertIn("URL inputs are intentionally not fetched", result.stderr)
        self.assertFalse(output_dir.exists())


if __name__ == "__main__":
    unittest.main()
