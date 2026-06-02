# RISKS

Updated: 2026-06-02

## Confirmation Levels

- Low: reads, drafts, local analysis.
- Medium: local file generation, non-destructive scripts.
- High: credentials, runtime config, external writes, deletes, push, deploy, service restart.

## Active Risks

| ID | Risk | Impact | Mitigation | Confirmation |
|---|---|---|---|---|
| R001 | Source content is unavailable | The system may produce weak or invented notes | Require visible source text or write to inbox/failure report | Medium |
| R002 | External mirror writes incorrect content | Human-facing workspace becomes misleading | Dry-run first and require explicit confirmation for real writes | High |
| R003 | Credentials are committed | Security incident | Keep credentials out of repo and inspect git status before commit | High |

