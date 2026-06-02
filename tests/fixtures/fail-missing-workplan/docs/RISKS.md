# RISKS

Updated: 2026-06-02

## Confirmation Levels

- Low: reads and non-destructive checks.
- Medium: local file generation.
- High: external writes, deletes, push, publish, deploy, or service restart.

High-risk actions require explicit confirmation.

## Active Risks

| ID | Risk | Impact | Mitigation | Confirmation |
|---|---|---|---|---|
| R001 | Missing workplan | Codex lacks test contract | Doctor reports the missing file | Medium |
