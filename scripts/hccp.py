#!/usr/bin/env python3
"""Unified Hermes-Codex control-plane command line."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable


def run_command(command: list[str]) -> int:
    try:
        completed = subprocess.run(command, cwd=REPO_ROOT, check=False)
    except OSError as exc:
        print(f"Unable to run command: {exc}", file=sys.stderr)
        return 2
    return completed.returncode


def script_path(*parts: str) -> str:
    return str(REPO_ROOT.joinpath(*parts))


def command_doctor(args: argparse.Namespace) -> int:
    command = [
        PYTHON,
        script_path("scripts", "check_control_plane.py"),
        args.project_path,
    ]
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
    if args.input:
        command.extend(["--input", args.input])
    if args.output:
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


def command_install_skills(_args: argparse.Namespace) -> int:
    return run_command([script_path("scripts", "install_codex_skills.sh")])


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="hccp",
        description="Unified CLI for the Hermes-Codex control-plane starter kit.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    doctor = subparsers.add_parser("doctor", help="Check a target project against the 3+3 standard")
    doctor.add_argument("project_path", help="Project directory to check")
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
    install_skills.set_defaults(func=command_install_skills)

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
