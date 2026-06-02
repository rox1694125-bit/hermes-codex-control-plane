# Quickstart

## 1. Install Skills

From this repository:

```bash
./scripts/install_codex_skills.sh
```

This installs:

- `hermes-project-operating-manual`
- `hermes-architecture`

Restart Codex or start a fresh thread if your skill list is cached.

## 2. Initialize A Project

```bash
./scripts/init_project_standard.sh /path/to/project
```

The script writes files only when they do not already exist:

```text
AGENTS.md
PROJECT_BRIEF.md
WORKPLAN.md
docs/DECISIONS.md
docs/RISKS.md
docs/project-log/
```

Use `--force` only when you intentionally want to overwrite existing files.

## 3. Customize The Files

Edit:

- `PROJECT_BRIEF.md`: current state and boundaries;
- `WORKPLAN.md`: active tasks, acceptance criteria, and tests;
- `AGENTS.md`: project-specific confirmation rules and checks.

Keep them short. Move history and rationale into `docs/DECISIONS.md` and `docs/project-log/`.

## 4. Run The Doctor

```bash
python3 scripts/check_control_plane.py /path/to/project
```

Use the target project path. Do not run this command on the repository root unless the repository itself is the project being checked.

Expected behavior:

- `PASS`: no required errors were found.
- `Warnings`: placeholders, empty logs, or missing optional docs; useful to fix, but they do not fail and exit `0`.
- `FAIL`: required files, required sections, high-risk confirmation language, or safety hygiene need attention.

Exit codes:

- `0`: no errors, including warning-only projects;
- `1`: validation errors;
- `2`: usage or project-path errors.

For agent/CI consumers:

```bash
python3 scripts/check_control_plane.py /path/to/project --json
```

The JSON report includes `ok`, `project_path`, `errors`, `warnings`, and `summary`.

Try the bundled example:

```bash
python3 scripts/check_control_plane.py examples/knowledge-ingestion-agent
```

For maintainers of this repository:

```bash
python3 scripts/check_repo_package.py .
python3 tests/test_check_control_plane.py
python3 tests/test_check_repo_package.py
```

## 5. Start Codex

Use:

```text
启动 Hermes 开发控制台协议，项目：/path/to/project，任务：Implement the next ingestion smoke test
```

Codex should load the operating manual skill, read the project startup files, decide whether `hermes-architecture` is needed, and plan before editing.

## 6. Use Multi-Agent Carefully

The trigger phrase grants permission to use Codex subagents when useful. It does not bypass planning or confirmation.

Use subagents after:

- goal is clear;
- test scenarios are defined;
- file ownership is clear;
- high-risk actions are identified.
