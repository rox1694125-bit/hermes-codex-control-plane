#!/usr/bin/env python3
"""Check whether this repository is a complete Hermes-Codex public package."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

import check_control_plane


REQUIRED_FILES = (
    "README.md",
    "LICENSE",
    "SECURITY.md",
    "CONTRIBUTING.md",
    ".gitignore",
    "docs/quickstart.md",
    "docs/architecture.md",
    "docs/migration-guide.md",
    "docs/legacy-doc-mapping.md",
    "docs/roadmap.md",
    "docs/github-publication.md",
    "docs/positioning.md",
    "protocols/hermes-development-control-plane.md",
    "protocols/multi-agent-contract.md",
    "skills/hermes-project-operating-manual/SKILL.md",
    "skills/hermes-architecture/SKILL.md",
    "templates/project-standard/AGENTS.md",
    "templates/project-standard/PROJECT_BRIEF.md",
    "templates/project-standard/WORKPLAN.md",
    "templates/project-standard/docs/DECISIONS.md",
    "templates/project-standard/docs/RISKS.md",
    "examples/knowledge-ingestion-agent/AGENTS.md",
    "examples/knowledge-ingestion-agent/README.md",
    "examples/knowledge-ingestion-agent/PROJECT_BRIEF.md",
    "examples/knowledge-ingestion-agent/WORKPLAN.md",
    "examples/knowledge-ingestion-agent/docs/DECISIONS.md",
    "examples/knowledge-ingestion-agent/docs/RISKS.md",
    "examples/knowledge-ingestion-agent/fixtures/message-event.json",
    "examples/knowledge-ingestion-agent/fixtures/sample-article.txt",
    "examples/knowledge-ingestion-agent/scripts/run_demo.py",
    "scripts/check_control_plane.py",
    "scripts/check_repo_package.py",
    "scripts/hccp.py",
    "scripts/init_project_standard.sh",
    "scripts/install_codex_skills.sh",
    "tests/test_check_control_plane.py",
    "tests/test_check_repo_package.py",
    "tests/test_hccp_cli.py",
    "tests/test_runnable_demo.py",
)
REQUIRED_DIRS = (
    "templates/project-standard/docs/project-log",
    "examples/knowledge-ingestion-agent/docs/project-log",
    "tests/fixtures/pass-project",
    "tests/fixtures/warn-template-project",
    "tests/fixtures/fail-missing-workplan",
)
README_REFERENCES = (
    "scripts/check_control_plane.py",
    "scripts/check_repo_package.py",
    "scripts/hccp.py",
    "docs/architecture.md",
    "docs/migration-guide.md",
    "docs/legacy-doc-mapping.md",
    "templates/project-standard",
    "examples/knowledge-ingestion-agent",
)
SKILL_FILES = (
    "skills/hermes-project-operating-manual/SKILL.md",
    "skills/hermes-architecture/SKILL.md",
)
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
SKIP_FILES = {".DS_Store", "Thumbs.db"}
BINARY_EXTENSIONS = {
    ".7z",
    ".avif",
    ".db",
    ".doc",
    ".docx",
    ".gif",
    ".heic",
    ".ico",
    ".jpeg",
    ".jpg",
    ".key",
    ".m4a",
    ".mkv",
    ".mov",
    ".mp3",
    ".mp4",
    ".numbers",
    ".pages",
    ".pdf",
    ".png",
    ".ppt",
    ".pptx",
    ".sqlite",
    ".sqlite3",
    ".wav",
    ".webm",
    ".webp",
    ".xls",
    ".xlsx",
    ".zip",
}
TEXT_SAMPLE_BYTES = 8192
SECRET_DIRS = {"secrets", "credentials"}
RUNTIME_STATE_DIRS = {"profiles", "memories", "sessions"}
SECRET_FILE_SUFFIXES = (".pem", ".key", ".p12", ".pfx", ".crt", ".token")
ALLOWED_ENV_FILES = {".env.example"}
PRIVATE_PATH_RE = re.compile(r"/(?:Users|Volumes)/[^/\s`),\]}\"]+/[^\s`),\]}\"]+")
TOKEN_PATTERNS = (
    re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{16,}\b"),
)
SKILL_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SKILL_VERSION_RE = re.compile(r"^\d+\.\d+$")
MAX_SKILL_DESCRIPTION_LENGTH = 700


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


def should_skip(path: Path, root: Path) -> bool:
    try:
        parts = path.relative_to(root).parts
    except ValueError:
        parts = path.parts
    if parts and parts[0] == "demo-output":
        return True
    if len(parts) >= 3 and parts[0] == "examples" and parts[2] == "demo-output":
        return True
    return any(part in SKIP_DIRS for part in parts)


def should_scan_text(path: Path) -> bool:
    if path.name in SKIP_FILES:
        return False
    if path.suffix.lower() in BINARY_EXTENSIONS:
        return False
    try:
        with path.open("rb") as handle:
            sample = handle.read(TEXT_SAMPLE_BYTES)
    except OSError:
        return False
    if b"\0" in sample:
        return False
    try:
        sample.decode("utf-8")
    except UnicodeDecodeError:
        return False
    return True


def iter_repo_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if should_skip(path, root):
            continue
        if path.is_file():
            yield path


def check_structure(root: Path, errors: list[Finding]) -> None:
    for file_rel in REQUIRED_FILES:
        if not (root / file_rel).is_file():
            errors.append(Finding("missing_repo_file", f"Missing required repository file: {file_rel}", file_rel))

    for dir_rel in REQUIRED_DIRS:
        if not (root / dir_rel).is_dir():
            errors.append(Finding("missing_repo_dir", f"Missing required repository directory: {dir_rel}", dir_rel))


def check_readme(root: Path, errors: list[Finding]) -> None:
    readme = root / "README.md"
    if not readme.is_file():
        return

    content = read_text(readme)
    for reference in README_REFERENCES:
        if reference not in content:
            errors.append(Finding("missing_readme_reference", f"README.md should reference {reference}", "README.md"))


def frontmatter(content: str) -> tuple[dict[str, str], bool]:
    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, False

    metadata: dict[str, str] = {}
    closed = False
    for line in lines[1:]:
        if line.strip() == "---":
            closed = True
            break
        if ":" in line:
            key, value = line.split(":", 1)
            metadata[key.strip()] = value.strip()
    return metadata, closed


def check_skill_metadata(root: Path, errors: list[Finding]) -> None:
    for skill_rel in SKILL_FILES:
        path = root / skill_rel
        if not path.is_file():
            continue
        metadata, closed = frontmatter(read_text(path))
        if not closed:
            errors.append(Finding("invalid_skill_frontmatter", f"{skill_rel} frontmatter must start and end with ---", skill_rel))
        for key in ("name", "description", "version", "status"):
            if not metadata.get(key):
                errors.append(Finding("missing_skill_metadata", f"{skill_rel} missing frontmatter key: {key}", skill_rel))
        if metadata.get("name") and SKILL_NAME_RE.fullmatch(metadata["name"]) is None:
            errors.append(Finding("invalid_skill_name", f"{skill_rel} frontmatter name should be a lowercase slug", skill_rel))
        description = metadata.get("description", "")
        if "\n" in description or len(description) > MAX_SKILL_DESCRIPTION_LENGTH:
            errors.append(
                Finding(
                    "invalid_skill_description",
                    f"{skill_rel} frontmatter description should be a concise single line",
                    skill_rel,
                )
            )
        if metadata.get("version") and SKILL_VERSION_RE.fullmatch(metadata["version"]) is None:
            errors.append(Finding("invalid_skill_version", f"{skill_rel} frontmatter version should look like N.N", skill_rel))
        if metadata.get("status") and metadata["status"] != "public-pattern":
            errors.append(
                Finding(
                    "skill_status_mismatch",
                    f"{skill_rel} frontmatter status should be public-pattern",
                    skill_rel,
                )
            )
        expected_name = path.parent.name
        if metadata.get("name") and metadata["name"] != expected_name:
            errors.append(
                Finding(
                    "skill_name_mismatch",
                    f"{skill_rel} frontmatter name should match directory: {expected_name}",
                    skill_rel,
                )
            )


def check_script_references(root: Path, errors: list[Finding]) -> None:
    install_script = root / "scripts" / "install_codex_skills.sh"
    if install_script.is_file():
        content = read_text(install_script)
        installed_skills = set(re.findall(r'install_skill\s+"([^"]+)"', content))
        expected_skills = {Path(skill_rel).parent.name for skill_rel in SKILL_FILES}
        for skill_name in sorted(installed_skills):
            if not (root / "skills" / skill_name / "SKILL.md").is_file():
                errors.append(
                    Finding(
                        "install_references_missing_skill",
                        f"install_codex_skills.sh references missing skill: {skill_name}",
                        "scripts/install_codex_skills.sh",
                    )
                )
        for skill_name in sorted(expected_skills - installed_skills):
            errors.append(
                Finding(
                    "skill_not_installed",
                    f"install_codex_skills.sh should install skill: {skill_name}",
                    "scripts/install_codex_skills.sh",
                )
            )

    init_script = root / "scripts" / "init_project_standard.sh"
    if init_script.is_file():
        content = read_text(init_script)
        copied_files = set(re.findall(r'copy_file\s+"([^"]+)"', content))
        for file_rel in sorted(copied_files):
            template_path = root / "templates" / "project-standard" / file_rel
            if not template_path.is_file():
                errors.append(
                    Finding(
                        "init_references_missing_template",
                        f"init_project_standard.sh references missing template file: {file_rel}",
                        "scripts/init_project_standard.sh",
                    )
                )


def check_doctor_targets(root: Path, errors: list[Finding], warnings: list[Finding]) -> None:
    example_report = check_control_plane.run_check(root / "examples" / "knowledge-ingestion-agent")
    if example_report["errors"]:
        errors.append(Finding("example_doctor_failed", "Example project should pass the control-plane doctor", "examples/knowledge-ingestion-agent"))
    if example_report["warnings"]:
        warnings.append(Finding("example_doctor_warned", "Example project should stay warning-free", "examples/knowledge-ingestion-agent"))

    template_report = check_control_plane.run_check(root / "templates" / "project-standard")
    if template_report["errors"]:
        errors.append(Finding("template_doctor_failed", "Project template should not fail the control-plane doctor", "templates/project-standard"))


def check_safety(root: Path, errors: list[Finding]) -> None:
    for path in root.rglob("*"):
        if should_skip(path, root):
            continue
        relative = rel(path, root)

        if path.is_dir() and path.name.lower() in SECRET_DIRS:
            errors.append(Finding("secret_dir", f"Secret-bearing directory should not be committed: {relative}", relative))
            continue
        if path.is_dir() and path.name.lower() in RUNTIME_STATE_DIRS:
            errors.append(Finding("runtime_state_dir", f"Runtime state directory should not be committed: {relative}", relative))
            continue

        if not path.is_file():
            continue

        name = path.name.lower()
        if (name == ".env" or name.startswith(".env.")) and name not in ALLOWED_ENV_FILES:
            errors.append(Finding("secret_file", f"Secret-bearing file should not be committed: {relative}", relative))
        if name.endswith(SECRET_FILE_SUFFIXES):
            errors.append(Finding("secret_file", f"Secret-bearing file should not be committed: {relative}", relative))

        if not should_scan_text(path):
            continue

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


def run_check(repo_path: Path) -> dict:
    root = repo_path.resolve()
    errors: list[Finding] = []
    warnings: list[Finding] = []

    if not root.exists():
        return {
            "ok": False,
            "repo_path": str(root),
            "errors": [asdict(Finding("missing_repo", f"Repository path does not exist: {root}"))],
            "warnings": [],
            "summary": {"errors": 1, "warnings": 0},
        }
    if not root.is_dir():
        return {
            "ok": False,
            "repo_path": str(root),
            "errors": [asdict(Finding("not_a_directory", f"Repository path is not a directory: {root}"))],
            "warnings": [],
            "summary": {"errors": 1, "warnings": 0},
        }

    check_structure(root, errors)
    check_readme(root, errors)
    check_skill_metadata(root, errors)
    check_script_references(root, errors)
    check_doctor_targets(root, errors, warnings)
    check_safety(root, errors)

    return {
        "ok": not errors,
        "repo_path": str(root),
        "errors": [asdict(item) for item in errors],
        "warnings": [asdict(item) for item in warnings],
        "summary": {"errors": len(errors), "warnings": len(warnings)},
    }


def print_human(report: dict) -> None:
    status = "FAIL"
    if report["ok"]:
        status = "WARN" if report["warnings"] else "PASS"
    summary = report["summary"]
    print(f"Hermes-Codex Repo Linter: {status}")
    print(f"Repository: {report['repo_path']}")
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
    parser = argparse.ArgumentParser(description="Check whether this repository is a complete public package.")
    parser.add_argument("repo_path", nargs="?", default=".", help="Repository directory to check")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    parser.add_argument("--strict-warnings", action="store_true", help="Return exit 1 when warnings are present")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    try:
        args = parse_args(argv)
    except SystemExit as exc:
        return int(exc.code) if isinstance(exc.code, int) else 2

    report = run_check(Path(args.repo_path))
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_human(report)

    argument_error_codes = {"missing_repo", "not_a_directory"}
    if report["ok"]:
        return 1 if args.strict_warnings and report["warnings"] else 0
    if any(item["code"] in argument_error_codes for item in report["errors"]):
        return 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
