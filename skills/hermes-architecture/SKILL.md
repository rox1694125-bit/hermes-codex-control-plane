---
name: hermes-architecture
description: Load before changing Hermes Agent, Hermes profiles, gateway integrations, messaging-platform adapters such as Feishu/Lark, skills, tools, Codex runtime bridging, or Kanban worker behavior. Provides a compact architecture map, invariants, risk points, and test routing for Codex acting as the Hermes development control plane.
---

# Hermes Architecture

Use this skill whenever the task touches Hermes Agent itself, a Hermes-powered project, a messaging-platform gateway flow, a profile-specific runtime, skills/tooling, or multi-agent/Kanban behavior.

Codex is the development control plane. Hermes plus the messaging platform are the execution workers and user-facing runtime. Do not merge these roles unless the user explicitly asks for a runtime integration.

## First Moves

1. Read the repo or project `AGENTS.md` first when present.
2. If the task is medium or high risk, use planning plus grill-me before edits.
3. Define test scenarios before spawning workers or changing code.
4. Keep runtime boundaries clear: Codex edits and verifies; Hermes gateway/profile handles production execution.

## Architecture Map

- `run_agent.py`: top-level `AIAgent` surface and compatibility re-exports used by tests.
- `agent/system_prompt.py`: assembles stable, context, and volatile prompt tiers.
- `agent/prompt_builder.py`: builds skills index, environment hints, platform hints, project context, and `SOUL.md` identity.
- `agent/skill_utils.py`: lightweight skill metadata, frontmatter, disabled skill, platform, and external-dir utilities.
- `tools/skills_tool.py`: model-facing `skills_list` and `skill_view` tools plus local/plugin skill serving.
- `model_tools.py`, `tools/registry.py`, `toolsets.py`: tool registration, tool definitions, and toolset membership.
- `gateway/run.py`: long-lived gateway runtime, session routing, cached `AIAgent` instances, slash commands, background process handling, and embedded Kanban dispatcher.
- `gateway/platforms/feishu.py`: Feishu/Lark adapter. Normalizes SDK/webhook events into `MessageEvent`.
- `gateway/platforms/base.py`: base adapter pipeline and background processing wrapper.
- `hermes_cli/main.py`: CLI parser and command dispatch. Gateway service entry eventually runs `gateway.run.start_gateway`.
- `hermes_cli/gateway.py`: gateway command/service orchestration.
- `hermes_cli/kanban_db.py`: durable Kanban DB schema, task state machine, CAS claim, dispatcher, and worker spawning.
- `tools/kanban_tools.py`: structured worker/orchestrator tool surface for Kanban.
- `hermes_cli/kanban_swarm.py`: creates a Kanban DAG for root, workers, verifier, and synthesizer.
- `agent/transports/codex_app_server.py` and `agent/transports/hermes_tools_mcp_server.py`: Codex runtime bridge and Hermes tool exposure.

## Prompt And Context Rules

Hermes prompt assembly is intentionally layered and cached.

- `SOUL.md` from `HERMES_HOME` is identity, not project architecture.
- Project context priority is `.hermes.md`/`HERMES.md`, then `AGENTS.md`, then `CLAUDE.md`, then `.cursorrules`; first match wins.
- `.hermes.md` can hide `AGENTS.md` from Hermes because it has higher priority.
- Skills index enters the stable prompt only as names/descriptions. Full skill content requires `skill_view` or explicit preloading.
- External skills come from `skills.external_dirs`, but Codex does not automatically read Hermes `~/.hermes/skills`.
- `TERMINAL_CWD` matters in gateway mode because it controls project context and file/tool cwd.

## Messaging Gateway Flow

The Feishu/Lark adapter is a representative example of how messaging ingress reaches Hermes. Other adapters follow the same broad shape: platform event, normalized `MessageEvent`, base adapter pipeline, gateway runner, session, and `AIAgent`.

For normal chat messages:

1. `FeishuAdapter` receives SDK/webhook events.
2. `_on_message_event()` schedules `_handle_message_event_data()`.
3. `_handle_message_event_data()` deduplicates and checks admission.
4. `_process_inbound_message()` extracts text/media/mentions and creates `MessageEvent`.
5. `_dispatch_inbound_event()` applies batching.
6. `_handle_message_with_guards()` serializes per chat and calls the base adapter.
7. `BasePlatformAdapter.handle_message()` calls the registered `GatewayRunner._handle_message()`.
8. `GatewayRunner._handle_message_with_agent()` gets/creates a session and runs `AIAgent.run_conversation()`.

Feishu Drive comments are a separate route through `gateway/platforms/feishu_comment.py`; do not treat them as ordinary chat messages.

## Multi-Agent Boundaries

- Codex subagents are for current development work: exploration, bounded implementation, and verification.
- Hermes `delegate_task` is synchronous and not durable; use it for short in-turn child work inside Hermes.
- Hermes Kanban is durable and cross-profile; use it for long-running or multi-worker production workflows.
- messaging chat is an ingress surface, not a task-state protocol.
- Do not run multiple Kanban dispatchers against the same board.
- Do not modify Kanban SQLite directly; use `kanban_db.py`, CLI, dashboard, or `kanban_*` tools.

## High-Risk Changes

Ask for explicit confirmation before:

- editing profiles, `SOUL.md`, memory, cron, gateway config, `.env`, credentials, or allowlists;
- restarting gateway or changing launchd/systemd service behavior;
- performing real Feishu writes, external sends, deletes, migrations, push, or publish actions;
- changing prompt assembly, tool schemas, file safety, profile isolation, approval handling, or Kanban state transitions.

## Test Routing

Pick tests by touched area:

- Skills/context: `tests/skills`, `tests/run_agent/test_run_agent.py`, prompt size or context tests.
- Gateway/Feishu: targeted `tests/gateway` and adapter-specific tests.
- CLI/config/profile: `tests/hermes_cli`.
- Kanban: `tests/tools/test_kanban_tools.py`, `tests/hermes_cli/test_kanban*`, stress tests only when concurrency behavior changes.
- Desktop/Codex runtime bridge: relevant `apps/desktop` tests plus transport tests.

Always add or update tests when changing shared behavior, state transitions, prompt construction, tool schemas, or gateway routing.
