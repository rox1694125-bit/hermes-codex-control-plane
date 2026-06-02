# RISKS

Updated: 2026-06-02

## Confirmation Levels

- Low: reads, local analysis, and non-destructive checks.
- Medium: local file generation and local scripts.
- High: credentials, runtime config, external writes, deletes, push, publish, deploy, or service restart.

High-risk actions require explicit confirmation.

## Active Risks

| ID | Risk | Impact | Mitigation | Confirmation |
|---|---|---|---|---|
| R001 | Accidental external action | Public fixture behavior becomes misleading | Keep tests local-only | High |
