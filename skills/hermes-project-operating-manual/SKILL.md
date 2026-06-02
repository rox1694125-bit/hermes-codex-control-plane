---
name: hermes-project-operating-manual
description: Use when the user invokes a Hermes/Codex development-control-plane workflow, including phrases like "启动 Hermes 开发控制台协议", or asks Codex to work on any Hermes + messaging-platform project. Defines the 3+3 project file standard, planning/grill-me gate, multi-agent startup protocol, risk confirmation rules, and context-loading order.
---

# Hermes Project Operating Manual

This skill defines the standard way Codex acts as the development control plane for projects operated by Hermes plus a messaging platform such as Feishu/Lark, Slack, Telegram, or WeCom.

Trigger phrases include:

- "启动 Hermes 开发控制台协议"
- "按 Hermes 开发控制台模式处理..."
- "用 Codex 搭建/修复/优化 Hermes 加消息平台项目..."

## Role Contract

Codex is the development control plane:

- reads code and project docs;
- edits code and project files;
- runs tests and verification;
- uses Codex subagents for exploration, implementation, and verification.

Hermes plus the messaging platform are the execution workers:

- the messaging platform is the human-facing ingress and operating surface;
- Hermes profiles, gateway, tools, skills, and Kanban execute daily workflows;
- do not put Codex directly into the live message flow unless the user explicitly requests that architecture.

## Startup Protocol

When the user invokes the protocol:

1. Load this skill.
2. If the task touches Hermes internals, gateway adapters, profiles, skills, tools, Codex runtime, or Kanban, also load `hermes-architecture`.
3. Resolve the project path or ask only if it cannot be inferred.
4. Read the project `AGENTS.md`.
5. Read the mandatory 3 project context files if they exist:
   - `PROJECT_BRIEF.md`
   - `WORKPLAN.md`
   - latest file in `docs/project-log/`
6. Read optional docs only when needed:
   - `docs/DECISIONS.md`
   - `docs/RISKS.md`
   - `docs/SOURCE_POLICY.md`
   - `docs/TERMS.md`
7. Classify the task as explore, plan, implement, fix, review, verify, or migrate.
8. For medium/high-risk or ambiguous work, do planning plus grill-me before edits.
9. Define test scenarios before spawning workers or changing files.

## 3+3 Project Standard

Default project structure:

```text
AGENTS.md
PROJECT_BRIEF.md
WORKPLAN.md
docs/DECISIONS.md
docs/RISKS.md
docs/project-log/
```

Optional, domain-specific docs:

```text
docs/SOURCE_POLICY.md
docs/TERMS.md
```

File responsibilities:

- `AGENTS.md`: model-facing startup protocol, read order, risk rules, high-risk confirmations, and project-specific working discipline.
- `PROJECT_BRIEF.md`: compact current-state truth source. It replaces scattered status/continuity files as the default startup read.
- `WORKPLAN.md`: task truth source, acceptance criteria, test scenarios, and active plan.
- `docs/DECISIONS.md`: durable decisions and reasons, not a diary.
- `docs/RISKS.md`: active risk register and confirmation rules.
- `docs/project-log/`: chronological work log. Read only the latest entry during startup unless history is needed.
- `docs/SOURCE_POLICY.md`: content/source/legal/platform boundaries when the project collects or transforms external material.
- `docs/TERMS.md`: domain vocabulary and learning baseline for knowledge-heavy projects.

Avoid maintaining many empty files. Add optional docs only when they have real content and a clear maintenance owner.

## Planning And Grill-Me Gate

Before significant development, produce and align:

- goal and non-goals;
- affected files/modules;
- high-risk actions that need explicit confirmation;
- test cases and smoke scenarios;
- rollback or recovery path;
- multi-agent split, if any.

Use grill-me one question at a time when decisions are still open. Do not send workers into an underspecified task.

## Multi-Agent Startup

Using "启动 Hermes 开发控制台协议" authorizes Codex to use subagents when useful. High-risk actions still require separate confirmation.

Use this split:

- `explorer`: read-only codebase or doc questions with concrete outputs.
- `worker`: bounded implementation in disjoint files or modules.
- `verifier`: test, review, or risk-check work after implementation is ready.

Every worker prompt must state:

- owned files/modules;
- files/modules it must not touch;
- acceptance criteria;
- required tests;
- expected final summary format;
- warning that other agents or the user may be editing the codebase.

Do not use subagents for work that blocks the immediate next step and must be done locally.

## Risk Rules

Always ask for explicit confirmation before:

- profile, `SOUL.md`, memory, cron, gateway, `.env`, credential, or allowlist changes;
- real Feishu writes or external sends;
- deleting, migrating, or overwriting durable knowledge;
- restart/start/stop of gateway or services;
- commit, push, publish, or production deployment;
- actions outside the declared project boundary.

Low-risk reads, draft docs, local checks, and non-destructive planning can proceed.

## Output Discipline

At the end of a development turn, report:

- changed files;
- tests/checks run;
- high-risk actions avoided or still requiring confirmation;
- next concrete step.

If the project has a `WORKPLAN.md` or project log convention, update it when the work materially changes project state.
