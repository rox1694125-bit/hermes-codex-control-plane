# Architecture

Hermes-Codex Control Plane separates development control from live runtime execution.

## System Map

```mermaid
flowchart TB
    subgraph Control["Codex Development Control Plane"]
        Codex["Codex"]
        Skills["Codex skills<br/>hermes-project-operating-manual<br/>hermes-architecture"]
        Protocols["Protocols<br/>control-plane contract<br/>multi-agent contract"]
        Doctor["Verification<br/>project doctor<br/>repo linter<br/>tests"]
        Demo["Runnable local demo<br/>standard library only"]
    end

    subgraph Context["Shared Project Context"]
        Agents["AGENTS.md"]
        Brief["PROJECT_BRIEF.md"]
        Workplan["WORKPLAN.md"]
        Decisions["docs/DECISIONS.md"]
        Risks["docs/RISKS.md"]
        Log["docs/project-log/"]
    end

    subgraph Runtime["Hermes Runtime Execution Layer"]
        Gateway["Gateway"]
        Profiles["Profiles"]
        Tools["Tools and skills"]
        Memory["Memory"]
        Kanban["Kanban workers"]
    end

    subgraph Surface["Human Operating Surface"]
        Messaging["Messaging platform<br/>Feishu/Lark, Slack, Telegram, WeCom"]
        Human["Human operator"]
    end

    Human --> Messaging
    Messaging --> Gateway
    Gateway --> Profiles
    Profiles --> Tools
    Profiles --> Memory
    Profiles --> Kanban

    Codex --> Skills
    Codex --> Protocols
    Codex --> Doctor
    Codex --> Demo
    Codex <--> Context
    Context -. "configured project context" .-> Runtime
```

## Boundary Rules

- Codex edits, tests, reviews, documents, and coordinates development agents.
- Hermes profiles, gateway, tools, memory, and Kanban execute runtime workflows.
- Messaging platforms are ingress and operating surfaces, not development-control state.
- Skills carry durable architecture and operating knowledge.
- Project files carry current project truth and verification contracts.
- Doctor scripts check structure and safety before a project becomes a reliable control-plane target.
- Runtime-sensitive changes require explicit confirmation before Codex touches profiles, gateway config, credentials, live sends, deletes, restarts, pushes, publishes, or deployments.

## Data Flow

1. A human triggers work through Codex by naming the project and task.
2. Codex loads the operating manual skill and reads the 3+3 project context.
3. Codex plans, uses Explorer/Worker/Verifier agents when useful, edits files, and runs checks.
4. Hermes continues to run the live workflow through its own gateway/profile/runtime layer.
5. High-risk runtime actions require explicit confirmation before Codex touches them.

## What Stays Local

The bundled runnable demo is intentionally local-only:

- no URL fetching;
- no external API calls;
- no messaging sends;
- no credential edits;
- no Hermes gateway start or restart.

This makes it safe as a public example and useful as a smoke test for the operating pattern.
