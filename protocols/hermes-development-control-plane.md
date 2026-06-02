# Hermes Development Control Plane Protocol

## Role Split

Codex is the development control plane:

- reads architecture and project context;
- asks planning questions when needed;
- edits files;
- runs tests and verification;
- coordinates subagents for development work.

Hermes + Feishu/Lark are the runtime execution workers:

- Feishu/Lark is the human-facing operating surface;
- Hermes profiles, gateway, tools, skills, memory, and Kanban run daily workflows;
- runtime changes require explicit confirmation.

## Invocation

Example user phrase:

```text
启动 Hermes 开发控制台协议，项目：<project path or name>，任务：<goal>
```

Teams can localize or rename the trigger phrase. Invoking the agreed trigger grants Codex permission to load relevant skills and use subagents as needed. It does not authorize high-risk actions.

## Startup Sequence

1. Load `hermes-project-operating-manual`.
2. Load `hermes-architecture` if the work touches Hermes internals, Feishu gateway, profiles, skills, tools, Codex runtime, or Kanban.
3. Resolve project path.
4. Read project `AGENTS.md`.
5. Read `PROJECT_BRIEF.md`.
6. Read `WORKPLAN.md`.
7. Read latest `docs/project-log/YYYY-MM-DD.md` if it exists.
8. Read optional docs only as needed: `docs/DECISIONS.md`, `docs/RISKS.md`, `docs/SOURCE_POLICY.md`, `docs/TERMS.md`.
9. Classify the task and decide whether planning/grill-me is required.
10. Define test scenarios before edits or worker spawn.

## Planning Gate

Planning plus grill-me is required when:

- task scope is unclear;
- work is medium/high risk;
- multiple agents will write files;
- Hermes profile/gateway/runtime changes are possible;
- real Feishu writes or external sends are possible;
- tests/acceptance criteria are not obvious.

The plan must identify:

- goal and non-goals;
- files/modules likely touched;
- risk level and confirmation points;
- test scenarios;
- multi-agent split, if any;
- rollback/recovery path for risky changes.

## Risk Confirmation

Ask for explicit confirmation before:

- editing Hermes profiles, SOUL, memory, cron, gateway config, `.env`, credentials, or allowlists;
- restarting gateway or services;
- real Feishu writes or external sends;
- deleting, overwriting, or migrating durable knowledge;
- committing, pushing, publishing, or deploying;
- writing outside the declared project boundary.

## Completion Report

Every development turn should report:

- changed files;
- checks/tests run;
- skipped checks and why;
- high-risk actions avoided or pending confirmation;
- next concrete step.
