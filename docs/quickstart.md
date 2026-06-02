# Quickstart

## 1. Install Skills

From this repository:

```bash
python3 scripts/hccp.py install-skills
```

This installs:

- `hermes-project-operating-manual`
- `hermes-architecture`

Check the installation:

```bash
python3 scripts/hccp.py skill-status
```

`PASS` means the bundled skill metadata matches the installed `SKILL.md` files. `FAIL` means a skill is missing or the installed metadata is stale. To check without writing files, use:

```bash
python3 scripts/hccp.py install-skills --check --json
```

Restart Codex or start a fresh thread if your skill list is cached.

## 2. Initialize A Project

```bash
python3 scripts/hccp.py init /path/to/project
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

Migrating an existing project with older status or continuity docs? Read `docs/migration-guide.md` before forcing overwrites.

## 3. Customize The Files

Edit:

- `PROJECT_BRIEF.md`: current state and boundaries;
- `WORKPLAN.md`: active tasks, acceptance criteria, and tests;
- `AGENTS.md`: project-specific confirmation rules and checks.

Keep them short. Move history and rationale into `docs/DECISIONS.md` and `docs/project-log/`.

## 4. Run The Doctor

```bash
python3 scripts/hccp.py doctor /path/to/project
```

Use the target project path. Do not run this command on the repository root unless the repository itself is the project being checked.

Expected behavior:

- `PASS`: no errors or warnings were found.
- `WARN`: placeholders or empty logs; useful to fix, but they do not fail and exit `0` by default.
- `FAIL`: required files, required sections, high-risk confirmation language, or safety hygiene need attention.

Exit codes:

- `0`: no errors, including warning-only projects by default;
- `1`: validation errors, or warnings when `--strict-warnings` is used;
- `2`: usage or project-path errors.

For agent/CI consumers:

```bash
python3 scripts/hccp.py doctor /path/to/project --json
```

The JSON report includes `ok`, `project_path`, `errors`, `warnings`, and `summary`. `ok` means there are no validation errors; under `--strict-warnings`, warning-only reports still have `ok: true` but the process exits `1`.

Use `--strict-warnings` when warnings should block a release or CI-style check.

Try the bundled example:

```bash
python3 scripts/hccp.py doctor examples/knowledge-ingestion-agent
python3 scripts/hccp.py demo --json
```

For maintainers of this repository:

```bash
python3 scripts/hccp.py repo-doctor . --strict-warnings
python3 tests/test_hccp_cli.py
python3 tests/test_check_control_plane.py
python3 tests/test_check_repo_package.py
python3 tests/test_runnable_demo.py
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
