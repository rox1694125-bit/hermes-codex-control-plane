# AGENTS.md

Project startup instructions for Codex/Hermes.

## Operating Mode

Use the Hermes development control plane model:

- Codex reads, plans, edits, tests, and verifies.
- Hermes + the messaging platform are runtime execution workers.
- Do not connect Codex directly into live messaging flows unless explicitly requested.

When the user says "启动 Hermes 开发控制台协议", load `hermes-project-operating-manual`. If the work touches Hermes internals, messaging-platform gateways, profiles, skills, tools, Codex runtime, or Kanban, also load `hermes-architecture`.

## Required Startup Reads

Read these first:

1. `PROJECT_BRIEF.md`
2. `WORKPLAN.md`
3. latest `docs/project-log/YYYY-MM-DD.md` if present

Read these only as needed:

- `docs/DECISIONS.md`
- `docs/RISKS.md`
- `docs/SOURCE_POLICY.md`
- `docs/TERMS.md`

## Planning Gate

Before medium/high-risk work or multi-agent implementation:

1. clarify goal and non-goals;
2. use grill-me when decisions are not locked;
3. define acceptance criteria and test scenarios;
4. identify high-risk confirmation points;
5. only then spawn workers or edit files.

## High-Risk Actions

Ask for explicit confirmation before:

- real external writes/sends;
- deleting, overwriting, or migrating durable data;
- profile, memory, gateway, cron, config, `.env`, credential, or allowlist changes;
- service restarts;
- commit, push, publish, or deploy;
- writing outside this project.

## Checks

List project-specific checks here.

```bash
# example
python3 scripts/check_handoff.py
```
