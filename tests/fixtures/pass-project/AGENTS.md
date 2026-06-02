# AGENTS.md

Startup instructions for a compliant Hermes-Codex control-plane project.

## Operating Mode

Codex is the development control plane. Hermes and the messaging platform remain the runtime execution layer.

## Required Startup Reads

Read these first:

1. `PROJECT_BRIEF.md`
2. `WORKPLAN.md`
3. latest dated file in `docs/project-log/` if present

Read as needed:

- `docs/DECISIONS.md`
- `docs/RISKS.md`
- `docs/SOURCE_POLICY.md`
- `docs/TERMS.md`

## High-Risk Actions

Ask for explicit confirmation before credential edits, runtime config changes, external writes, deletes, pushes, publishes, deployments, or service restarts.

## Checks

```bash
python3 scripts/check_control_plane.py .
```
