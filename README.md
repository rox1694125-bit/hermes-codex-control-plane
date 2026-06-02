# Hermes-Codex Control Plane

A public, reusable operating pattern for using Codex as the development control plane for Hermes-powered messaging-agent systems.

The core split is simple:

- **Codex builds the system**: architecture, code changes, tests, reviews, and multi-agent development coordination.
- **Hermes runs the system**: profiles, gateway, tools, skills, memory, Kanban, and messaging-platform execution.
- **Messaging apps are the operating surface**: Feishu/Lark, Slack, Telegram, WeCom, or similar platforms are how humans trigger and consume the runtime.

This project turns that split into skills, protocols, templates, and scripts that other builders can copy.

## Why This Exists

Agent projects often fail for boring reasons:

- every new thread has to rediscover the architecture;
- project context is scattered across chats and stale docs;
- multi-agent work starts before tests and acceptance criteria are clear;
- live runtime changes get mixed with development work;
- long-running messaging-agent systems accumulate profile, gateway, credential, and memory risk.

This repo proposes a small standard:

1. put stable architecture knowledge in Codex skills;
2. put project truth in a compact 3+3 file structure;
3. require a planning and test gate before multi-agent implementation;
4. keep development control separate from live runtime execution.

## Quick Start

Install the Codex skills:

```bash
./scripts/install_codex_skills.sh
```

Initialize the standard files in a project:

```bash
./scripts/init_project_standard.sh /path/to/your-project
```

Then start a Codex session with:

```text
启动 Hermes 开发控制台协议，项目：/path/to/your-project，任务：<what you want to change>
```

This trigger phrase means Codex may load the relevant skills and use subagents when useful. It does **not** authorize high-risk runtime actions such as real external writes, credential edits, gateway restarts, deletes, pushes, or deployments.

## What You Get

- `skills/hermes-project-operating-manual/`: startup protocol, 3+3 project standard, planning gate, multi-agent rules.
- `skills/hermes-architecture/`: Hermes runtime architecture map and risk/test routing.
- `protocols/hermes-development-control-plane.md`: human-readable operating protocol.
- `protocols/multi-agent-contract.md`: explorer / worker / verifier contract for Codex subagents.
- `templates/project-standard/`: reusable project files.
- `examples/knowledge-ingestion-agent/`: sanitized example project using the standard.
- `scripts/install_codex_skills.sh`: installs skills into `~/.codex/skills`.
- `scripts/init_project_standard.sh`: initializes project files without overwriting by default.

## The 3+3 Project Standard

Default project files:

```text
AGENTS.md
PROJECT_BRIEF.md
WORKPLAN.md
docs/DECISIONS.md
docs/RISKS.md
docs/project-log/
```

Optional domain files:

```text
docs/SOURCE_POLICY.md
docs/TERMS.md
```

The point is not documentation for its own sake. The point is to keep the startup context small enough for models to read every time, while preserving deeper docs for decisions, risks, and history.

## Who This Is For

This is useful if you are building:

- a Hermes-based personal or team agent;
- a Feishu/Lark or Slack workflow agent;
- a content ingestion or knowledge-base agent;
- a multi-agent coding or operations workflow;
- any long-lived agent system where runtime execution and development work should stay separate.

## What This Is Not

This is not:

- a replacement for Hermes;
- a live messaging gateway;
- a credential manager;
- a promise that Codex should operate production systems directly;
- a one-size-fits-all project-management methodology.

It is an operating pattern and starter kit.

## Recommended Rollout

1. Install the skills.
2. Initialize one non-critical project with the 3+3 standard.
3. Run several real development sessions using the trigger phrase.
4. Adjust the templates to your organization.
5. Only then migrate older, more complex projects.

## Status

Public v0.1 packaging is in progress. The current focus is making the pattern understandable, reusable, and safe before adding heavier automation.
