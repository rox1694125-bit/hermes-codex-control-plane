#!/usr/bin/env python3
"""Unified Hermes-Codex control-plane command line."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable
BUNDLED_SKILLS = ("hermes-project-operating-manual", "hermes-architecture")


@dataclass
class Finding:
    code: str
    message: str
    path: str | None = None


def run_command(command: list[str]) -> int:
    try:
        completed = subprocess.run(command, cwd=REPO_ROOT, check=False)
    except OSError as exc:
        print(f"Unable to run command: {exc}", file=sys.stderr)
        return 2
    return completed.returncode


def script_path(*parts: str) -> str:
    return str(REPO_ROOT.joinpath(*parts))


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


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


def codex_home() -> Path:
    return Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser()


def skill_status_report() -> dict:
    home = codex_home()
    target_root = home / "skills"
    errors: list[Finding] = []
    warnings: list[Finding] = []
    skills: list[dict] = []

    for skill_name in BUNDLED_SKILLS:
        source_path = REPO_ROOT / "skills" / skill_name / "SKILL.md"
        installed_path = target_root / skill_name / "SKILL.md"

        if not source_path.is_file():
            errors.append(Finding("missing_skill_source", f"Missing bundled skill source: {skill_name}", str(source_path)))
            skills.append(
                {
                    "name": skill_name,
                    "status": "missing-source",
                    "source": str(source_path),
                    "installed_path": str(installed_path),
                    "expected_version": None,
                    "installed_version": None,
                    "message": "Bundled skill source is missing.",
                }
            )
            continue

        source_metadata, source_closed = frontmatter(read_text(source_path))
        expected_version = source_metadata.get("version")
        expected_status = source_metadata.get("status")
        if not source_closed:
            errors.append(Finding("invalid_skill_source", f"Bundled skill has invalid frontmatter: {skill_name}", str(source_path)))

        if not installed_path.is_file():
            errors.append(Finding("missing_installed_skill", f"Skill is not installed: {skill_name}", str(installed_path)))
            skills.append(
                {
                    "name": skill_name,
                    "status": "missing",
                    "source": str(source_path),
                    "installed_path": str(installed_path),
                    "expected_version": expected_version,
                    "installed_version": None,
                    "message": "Run `python3 scripts/hccp.py install-skills` to install this skill.",
                }
            )
            continue

        installed_metadata, installed_closed = frontmatter(read_text(installed_path))
        installed_version = installed_metadata.get("version")
        mismatches: list[str] = []
        if not installed_closed:
            mismatches.append("frontmatter")
        for key in ("name", "description", "version", "status"):
            if installed_metadata.get(key) != source_metadata.get(key):
                mismatches.append(key)

        if mismatches:
            errors.append(
                Finding(
                    "installed_skill_mismatch",
                    f"Installed skill differs from bundled source: {skill_name} ({', '.join(mismatches)})",
                    str(installed_path),
                )
            )
            skills.append(
                {
                    "name": skill_name,
                    "status": "mismatch",
                    "source": str(source_path),
                    "installed_path": str(installed_path),
                    "expected_version": expected_version,
                    "installed_version": installed_version,
                    "expected_status": expected_status,
                    "installed_status": installed_metadata.get("status"),
                    "mismatches": mismatches,
                    "message": "Re-run `python3 scripts/hccp.py install-skills` to refresh this skill.",
                }
            )
            continue

        skills.append(
            {
                "name": skill_name,
                "status": "current",
                "source": str(source_path),
                "installed_path": str(installed_path),
                "expected_version": expected_version,
                "installed_version": installed_version,
                "expected_status": expected_status,
                "installed_status": installed_metadata.get("status"),
                "message": "Installed skill matches the bundled source metadata.",
            }
        )

    status_counts = {status: 0 for status in ("current", "missing", "mismatch", "missing-source")}
    for skill in skills:
        status_counts[skill["status"]] = status_counts.get(skill["status"], 0) + 1

    return {
        "ok": not errors,
        "codex_home": str(home),
        "skills_path": str(target_root),
        "skills": skills,
        "errors": [asdict(item) for item in errors],
        "warnings": [asdict(item) for item in warnings],
        "summary": {
            "errors": len(errors),
            "warnings": len(warnings),
            "skills": len(skills),
            "current": status_counts.get("current", 0),
            "missing": status_counts.get("missing", 0),
            "mismatch": status_counts.get("mismatch", 0),
            "missing_source": status_counts.get("missing-source", 0),
        },
    }


def print_skill_status(report: dict) -> None:
    status = "PASS" if report["ok"] else "FAIL"
    summary = report["summary"]
    print(f"Hermes-Codex Skill Status: {status}")
    print(f"CODEX_HOME: {report['codex_home']}")
    print(f"Skills path: {report['skills_path']}")
    print(
        "Skills: "
        f"{summary['skills']}  Current: {summary['current']}  "
        f"Missing: {summary['missing']}  Mismatch: {summary['mismatch']}"
    )

    for skill in report["skills"]:
        version = skill.get("installed_version") or "not installed"
        expected = skill.get("expected_version") or "unknown"
        print(f"- {skill['name']}: {skill['status']} (installed: {version}, expected: {expected})")

    if report["errors"]:
        print("\nErrors")
        for item in report["errors"]:
            location = f" [{item['path']}]" if item.get("path") else ""
            print(f"- {item['code']}{location}: {item['message']}")


def command_doctor(args: argparse.Namespace) -> int:
    command = [
        PYTHON,
        script_path("scripts", "check_control_plane.py"),
        args.project_path,
    ]
    if args.config is not None:
        command.extend(["--config", args.config])
    if args.json:
        command.append("--json")
    if args.strict_warnings:
        command.append("--strict-warnings")
    return run_command(command)


def command_repo_doctor(args: argparse.Namespace) -> int:
    command = [
        PYTHON,
        script_path("scripts", "check_repo_package.py"),
        args.repo_path,
    ]
    if args.json:
        command.append("--json")
    if args.strict_warnings:
        command.append("--strict-warnings")
    return run_command(command)


def command_demo(args: argparse.Namespace) -> int:
    command = [
        PYTHON,
        script_path("examples", "knowledge-ingestion-agent", "scripts", "run_demo.py"),
    ]
    if args.input is not None:
        command.extend(["--input", args.input])
    if args.output is not None:
        command.extend(["--output", args.output])
    if args.json:
        command.append("--json")
    return run_command(command)


def command_init(args: argparse.Namespace) -> int:
    command = [
        script_path("scripts", "init_project_standard.sh"),
        args.project_path,
    ]
    if args.force:
        command.append("--force")
    return run_command(command)


def command_skill_status(args: argparse.Namespace) -> int:
    report = skill_status_report()
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_skill_status(report)
    return 0 if report["ok"] else 1


def command_install_skills(args: argparse.Namespace) -> int:
    if args.check:
        return command_skill_status(args)
    if args.json:
        print("--json is only supported with install-skills --check", file=sys.stderr)
        return 2
    return run_command([script_path("scripts", "install_codex_skills.sh")])


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="hccp",
        description="Unified CLI for the Hermes-Codex control-plane starter kit.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    doctor = subparsers.add_parser("doctor", help="Check a target project against the 3+3 standard")
    doctor.add_argument("project_path", help="Project directory to check")
    doctor.add_argument("--config", help="Optional project config JSON path")
    doctor.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    doctor.add_argument("--strict-warnings", action="store_true", help="Return exit 1 when warnings are present")
    doctor.set_defaults(func=command_doctor)

    repo_doctor = subparsers.add_parser("repo-doctor", help="Check this public package repository")
    repo_doctor.add_argument("repo_path", nargs="?", default=".", help="Repository directory to check")
    repo_doctor.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    repo_doctor.add_argument("--strict-warnings", action="store_true", help="Return exit 1 when warnings are present")
    repo_doctor.set_defaults(func=command_repo_doctor)

    demo = subparsers.add_parser("demo", help="Run the local-only knowledge ingestion demo")
    demo.add_argument("--input", help="Local text source to ingest")
    demo.add_argument("--output", help="Directory for generated demo artifacts")
    demo.add_argument("--json", action="store_true", help="Print machine-readable run summary")
    demo.set_defaults(func=command_demo)

    init = subparsers.add_parser("init", help="Initialize the 3+3 project standard in a project")
    init.add_argument("project_path", help="Project directory to initialize")
    init.add_argument("--force", action="store_true", help="Overwrite existing standard files")
    init.set_defaults(func=command_init)

    install_skills = subparsers.add_parser("install-skills", help="Install bundled Codex skills")
    install_skills.add_argument("--check", action="store_true", help="Check installed skills without writing files")
    install_skills.add_argument("--json", action="store_true", help="Emit machine-readable JSON with --check")
    install_skills.set_defaults(func=command_install_skills)

    skill_status = subparsers.add_parser("skill-status", help="Check whether bundled Codex skills are installed and current")
    skill_status.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    skill_status.set_defaults(func=command_skill_status)

    return parser


def main(argv: list[str]) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code) if isinstance(exc.code, int) else 2
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
