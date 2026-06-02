# Positioning

## One Sentence

Hermes-Codex Control Plane is a reusable pattern for using Codex to build and maintain Hermes-powered messaging-agent systems without mixing development control with live runtime execution.

## Core Pattern

```text
Codex = development control plane
Hermes = runtime agent system
Messaging platform = human operating surface
Project docs + skills = shared context layer
```

## Design Principles

1. **Separate build from run.** Codex changes systems; Hermes runs them.
2. **Make context explicit.** Architecture belongs in skills; project state belongs in project files.
3. **Keep startup small.** Three required project files are enough for most sessions.
4. **Plan before parallelizing.** Multi-agent work starts only after scope and tests are clear.
5. **Treat runtime changes as high risk.** Profiles, gateways, credentials, external writes, and service restarts require explicit confirmation.

## Why Skills

Skills are the right place for durable architecture and operating knowledge because they are:

- triggerable by task description;
- reusable across projects;
- concise enough to load into context;
- versionable and reviewable.

Project-specific state should not live in skills. It belongs in `AGENTS.md`, `PROJECT_BRIEF.md`, `WORKPLAN.md`, and supporting docs.

## Why 3+3

The previous instinct in many agent projects is to create many specialized docs. That can work for humans, but models struggle when every startup requires reading ten or more files.

The 3+3 standard optimizes for model startup:

- `AGENTS.md`: how the agent should work here;
- `PROJECT_BRIEF.md`: what is true now;
- `WORKPLAN.md`: what to do and how to verify it;
- `docs/DECISIONS.md`: why durable choices were made;
- `docs/RISKS.md`: what needs caution;
- `docs/project-log/`: what happened over time.

Optional docs are added only when a domain truly needs them.

