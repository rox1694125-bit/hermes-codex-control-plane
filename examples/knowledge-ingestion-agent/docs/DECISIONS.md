# DECISIONS

Updated: 2026-06-02

## 2026-06-02: Keep Codex Out Of Runtime Message Flow

Decision:

Codex is used for development work only. Runtime messages are handled by Hermes and the messaging platform.

Reason:

This keeps debugging, credentials, external writes, and user-facing behavior inside the runtime system with explicit operational boundaries.

Consequences:

Codex can edit and verify the workflow, but real runtime writes require explicit confirmation and should be handled through Hermes.

