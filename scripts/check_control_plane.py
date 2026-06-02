#!/usr/bin/env python3
"""Check whether a project follows the Hermes-Codex control-plane standard."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable


REQUIRED_FILES = (
    "AGENTS.md",
    "PROJECT_BRIEF.md",
    "WORKPLAN.md",
    "docs/DECISIONS.md",
    "docs/RISKS.md",
)
REQUIRED_DIRS = ("docs/project-log",)

SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".cache",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    ".tox",
    ".nox",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    "dist",
    "build",
    "coverage",
}
SECRET_DIRS = {"secrets", "credentials"}
ALLOWED_ENV_FILES = {".env.example"}

PLACEHOLDER_RE = re.compile(r"<[^>\n]+>|YYYY-MM-DD")
PRIVATE_PATH_RE = re.compile(r"/(?:Users|Volumes)/[^/\s`)]+/[^\s`)]+")
TOKEN_PATTERNS = (
    re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{16,}\b"),
    re.compile(r"\bgho_[A-Za-z0-9_]{16,}\b"),
)


@dataclass
class Finding:
    code: str
    message: str
    path: str | None = None


def rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def has_all(content: str, needles: Iterable[str]) -> list[str]:
    lowered = content.lower()
    return [needle for needle in needles if needle.lower() not in lowered]


def has_high_risk_confirmation(content: str) -> bool:
    lowered = content.lower()
    has_risk = (
        "high-risk" in lowered
        or "high risk" in lowered
        or re.search(r"(?m)^\s*[-|]?\s*high\s*[:|]", lowered) is not None
    )
    has_confirm = (
        "explicit confirmation" in lowered
        or "require explicit" in lowered
        or "ask before" in lowered
        or "ask for explicit" in lowered
        or "requires confirmation" in lowered
        or "require confirmation" in lowered
    )
    return has_risk and has_confirm


def should_skip(path: Path, root: Path) -> bool:
    try:
        parts = path.relative_to(root).parts
    except ValueError:
        parts = path.parts
    return any(part in SKIP_DIRS for part in parts)


def iter_project_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if should_skip(path, root):
            continue
        if path.is_file():
            yield path


def check_structure(root: Path, errors: list[Finding], warnings: list[Finding]) -> None:
    for file_rel in REQUIRED_FILES:
        path = root / file_rel
        if not path.is_file():
            errors.append(Finding("missing_required_file", f"Missing required file: {file_rel}", file_rel))

    for dir_rel in REQUIRED_DIRS:
        path = root / dir_rel
        if not path.is_dir():
            errors.append(Finding("missing_required_dir", f"Missing required directory: {dir_rel}", dir_rel))
        elif not any(path.iterdir()):
            warnings.append(Finding("empty_project_log", f"Directory is empty: {dir_rel}", dir_rel))


def check_content(root: Path, errors: list[Finding], warnings: list[Finding]) -> None:
    agents = root / "AGENTS.md"
    if agents.is_file():
        content = read_text(agents)
        missing_refs = has_all(content, ("PROJECT_BRIEF.md", "WORKPLAN.md", "docs/RISKS.md"))
        for ref in missing_refs:
            errors.append(Finding("missing_startup_reference", f"AGENTS.md should reference {ref}", "AGENTS.md"))
        if not has_high_risk_confirmation(content):
            errors.append(
                Finding(
                    "missing_high_risk_confirmation",
                    "AGENTS.md should include high-risk confirmation language",
                    "AGENTS.md",
                )
            )

    brief = root / "PROJECT_BRIEF.md"
    if brief.is_file():
        content = read_text(brief)
        for section in ("One-Line State", "Scope", "Current Capabilities", "Current Next Steps", "Risk Summary"):
            if f"## {section}".lower() not in content.lower():
                errors.append(Finding("missing_section", f"PROJECT_BRIEF.md missing section: {section}", "PROJECT_BRIEF.md"))

    workplan = root / "WORKPLAN.md"
    if workplan.is_file():
        content = read_text(workplan)
        for section in ("Active Tasks", "Test Scenarios", "Required Checks"):
            if f"## {section}".lower() not in content.lower():
                errors.append(Finding("missing_section", f"WORKPLAN.md missing section: {section}", "WORKPLAN.md"))

    risks = root / "docs/RISKS.md"
    if risks.is_file():
        content = read_text(risks)
        for section in ("Confirmation Levels", "Active Risks"):
            if f"## {section}".lower() not in content.lower():
                errors.append(Finding("missing_section", f"docs/RISKS.md missing section: {section}", "docs/RISKS.md"))
        if not has_high_risk_confirmation(content):
            errors.append(
                Finding(
                    "missing_high_risk_confirmation",
                    "docs/RISKS.md should include high-risk confirmation language",
                    "docs/RISKS.md",
                )
            )

    for path in iter_project_files(root):
        try:
            content = read_text(path)
        except OSError:
            continue
        for match in PLACEHOLDER_RE.finditer(content):
            warnings.append(
                Finding(
                    "placeholder",
                    f"Template placeholder remains: {match.group(0)}",
                    rel(path, root),
                )
            )


def check_safety(root: Path, errors: list[Finding]) -> None:
    for path in root.rglob("*"):
        if should_skip(path, root):
            continue
        relative = rel(path, root)

        if path.is_dir() and path.name.lower() in SECRET_DIRS:
            errors.append(Finding("secret_dir", f"Secret-bearing directory should not be committed: {relative}", relative))
            continue

        if not path.is_file():
            continue

        name = path.name.lower()
        if (name == ".env" or name.startswith(".env.")) and name not in ALLOWED_ENV_FILES:
            errors.append(Finding("secret_file", f"Secret-bearing file should not be committed: {relative}", relative))

        try:
            content = read_text(path)
        except OSError:
            continue

        if PRIVATE_PATH_RE.search(content):
            errors.append(Finding("private_path", "Likely private local absolute path found", relative))

        for pattern in TOKEN_PATTERNS:
            if pattern.search(content):
                errors.append(Finding("token_like_secret", "Likely token-like secret found", relative))
                break


def run_check(project_path: Path) -> dict:
    root = project_path.resolve()
    errors: list[Finding] = []
    warnings: list[Finding] = []

    if not root.exists():
        return {
            "ok": False,
            "project_path": str(root),
            "errors": [asdict(Finding("missing_project", f"Project path does not exist: {root}"))],
            "warnings": [],
            "summary": {"errors": 1, "warnings": 0},
        }
    if not root.is_dir():
        return {
            "ok": False,
            "project_path": str(root),
            "errors": [asdict(Finding("not_a_directory", f"Project path is not a directory: {root}"))],
            "warnings": [],
            "summary": {"errors": 1, "warnings": 0},
        }

    check_structure(root, errors, warnings)
    check_content(root, errors, warnings)
    check_safety(root, errors)

    return {
        "ok": not errors,
        "project_path": str(root),
        "errors": [asdict(item) for item in errors],
        "warnings": [asdict(item) for item in warnings],
        "summary": {"errors": len(errors), "warnings": len(warnings)},
    }


def print_human(report: dict) -> None:
    status = "FAIL"
    if report["ok"]:
        status = "WARN" if report["warnings"] else "PASS"
    summary = report["summary"]
    print(f"Hermes-Codex Control Plane Doctor: {status}")
    print(f"Project: {report['project_path']}")
    print(f"Errors: {summary['errors']}  Warnings: {summary['warnings']}")

    if report["errors"]:
        print("\nErrors")
        for item in report["errors"]:
            location = f" [{item['path']}]" if item.get("path") else ""
            print(f"- {item['code']}{location}: {item['message']}")

    if report["warnings"]:
        print("\nWarnings")
        for item in report["warnings"]:
            location = f" [{item['path']}]" if item.get("path") else ""
            print(f"- {item['code']}{location}: {item['message']}")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check whether a project follows the Hermes-Codex 3+3 control-plane standard."
    )
    parser.add_argument("project_path", help="Project directory to check")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    parser.add_argument("--strict-warnings", action="store_true", help="Return exit 1 when warnings are present")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    try:
        args = parse_args(argv)
    except SystemExit as exc:
        return int(exc.code) if isinstance(exc.code, int) else 2

    report = run_check(Path(args.project_path))
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_human(report)

    argument_error_codes = {"missing_project", "not_a_directory"}
    if report["ok"]:
        return 1 if args.strict_warnings and report["warnings"] else 0
    if any(item["code"] in argument_error_codes for item in report["errors"]):
        return 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
