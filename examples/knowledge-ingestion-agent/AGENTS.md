# AGENTS.md

Startup instructions for a sample knowledge ingestion agent.

## Operating Mode

Use the Hermes development control plane model:

- Codex builds and verifies the ingestion system.
- Hermes runs the ingestion workflow.
- The messaging platform is the human-facing entry point.

When the user says "启动 Hermes 开发控制台协议", load `hermes-project-operating-manual`. Load `hermes-architecture` if the task touches Hermes gateway, profiles, tools, skills, or Kanban.

## Required Startup Reads

Read:

1. `PROJECT_BRIEF.md`
2. `WORKPLAN.md`
3. latest dated file in `docs/project-log/` if present

Read as needed:

- `docs/DECISIONS.md`
- `docs/RISKS.md`
- `docs/SOURCE_POLICY.md`
- `docs/TERMS.md`

## High-Risk Actions

Ask before:

- real external writes or messages;
- deleting or overwriting source material;
- editing runtime profile/gateway/config/credentials;
- pushing or deploying.

## Checks

Example checks:

```bash
python3 scripts/check_project.py
python3 scripts/build_indexes.py --check
```
