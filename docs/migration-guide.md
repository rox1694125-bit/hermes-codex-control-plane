# Migration Guide

Use this guide when an existing Hermes-powered project already has project notes, status files, continuity briefs, logs, or ad hoc operating rules and you want to migrate it into the Hermes-Codex 3+3 standard.

The migration goal is not to preserve every old file. The goal is to make Codex startup reliable:

- one clear startup protocol;
- one compact current-state brief;
- one active workplan with tests;
- durable decisions and risks in stable supporting docs;
- historical detail moved out of the startup path.

## Migration Principles

1. **Do not overwrite first.** Inventory old docs before running any forced init command.
2. **Preserve truth, remove duplication.** Keep one canonical home for each fact.
3. **Keep startup small.** Codex should usually read `AGENTS.md`, `PROJECT_BRIEF.md`, `WORKPLAN.md`, and the latest project log.
4. **Make risk explicit.** Runtime config, credentials, profile edits, gateway restarts, external writes, deletes, pushes, publishes, and deployments require confirmation.
5. **Verify the shape.** Run the Protocol Doctor after each migration pass.

## Recommended Migration Flow

### 1. Inventory Existing Files

List current project docs and classify each one:

- startup instructions;
- current state/status;
- active tasks;
- tests/checks;
- decisions/rationale;
- risks/permissions;
- source/content policy;
- glossary/domain terms;
- historical logs.

Do not move secrets, profiles, runtime memory, session stores, local browser data, or `.env` files into the public project tree.

### 2. Initialize Missing 3+3 Files

From this repository:

```bash
./scripts/init_project_standard.sh /path/to/project
```

Use `--force` only after you have backed up or intentionally replaced existing files.

There is no automatic migration script for legacy content. The init script creates missing standard files, but humans and Codex must summarize and route old content intentionally.

### 3. Merge Old Docs Into Canonical Homes

Use [legacy-doc-mapping.md](legacy-doc-mapping.md) as the routing table.

Default destinations:

- startup rules -> `AGENTS.md`;
- current state -> `PROJECT_BRIEF.md`;
- active tasks and tests -> `WORKPLAN.md`;
- durable decisions -> `docs/DECISIONS.md`;
- risks and permissions -> `docs/RISKS.md`;
- historical updates -> `docs/project-log/YYYY-MM-DD.md`;
- source/content boundaries -> `docs/SOURCE_POLICY.md`;
- domain terms -> `docs/TERMS.md`.

### 4. Keep Only Useful Optional Docs

Optional docs should have real content and a clear maintenance owner.

Create `docs/SOURCE_POLICY.md` when the project collects, summarizes, republishes, downloads, or transforms external content.

Create `docs/TERMS.md` when the domain has vocabulary that Codex must consistently understand.

Do not keep empty optional docs only to look complete.

### 5. Run The Doctor

```bash
python3 scripts/check_control_plane.py /path/to/project
```

Expected migration stages:

- Early migration may show `WARN` for placeholders or empty project logs.
- A ready project should show `PASS`.
- `FAIL` means required files, required sections, confirmation language, or safety hygiene need attention.

Use strict mode before treating the project as fully migrated:

```bash
python3 scripts/check_control_plane.py /path/to/project --strict-warnings
```

### 6. Start Codex With The Protocol

Once the Doctor passes, start a development-control session:

```text
启动 Hermes 开发控制台协议，项目：/path/to/project，任务：<goal>
```

For medium/high-risk work, define test scenarios before editing or spawning subagents.

## Migration Done Criteria

A migrated project is ready when:

- `AGENTS.md` names startup reads and high-risk confirmation rules;
- `PROJECT_BRIEF.md` explains current state, scope, capabilities, next steps, and risks;
- `WORKPLAN.md` lists active tasks, test scenarios, and required checks;
- `docs/RISKS.md` contains confirmation levels and active risks;
- old status/continuity files are either archived or clearly mapped;
- the Protocol Doctor returns `PASS`;
- no private paths, `.env` files, credentials, runtime state, or token-like secrets are committed.

## What Not To Migrate

Do not migrate these into the control-plane docs:

- real credentials or `.env` files;
- Hermes profile secrets;
- messaging-platform app secrets;
- memory/session stores;
- browser profiles or cookies;
- local absolute paths from a private machine;
- generated reports that contain private user/customer content;
- raw chat logs unless they have been sanitized and intentionally summarized.
