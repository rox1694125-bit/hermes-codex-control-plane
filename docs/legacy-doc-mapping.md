# Legacy Doc Mapping

Use this table to map older Hermes project documents into the 3+3 standard.

## Mapping Table

| Legacy doc or content | New home | Keep in startup path? | Notes |
|---|---|---|---|
| Project Continuity Brief | `PROJECT_BRIEF.md` | Yes | Keep only current state, scope, capabilities, next steps, and risk summary. Move history elsewhere. |
| Project Status | `WORKPLAN.md` or latest `docs/project-log/` | Yes for active tasks | Active work and tests go to `WORKPLAN.md`; completed updates go to the project log. |
| Current TODO list | `WORKPLAN.md` | Yes | Convert vague TODOs into tasks with acceptance criteria and test scenarios. |
| Acceptance criteria | `WORKPLAN.md` | Yes | Keep close to the task so workers can verify implementation. |
| Test checklist | `WORKPLAN.md` | Yes | Put commands under `Required Checks`; put manual scenarios under `Test Scenarios`. |
| Agent instructions | `AGENTS.md` | Yes | Include startup order, project discipline, and high-risk confirmation rules. |
| Prompt snippets | `AGENTS.md` or a skill | Sometimes | Stable cross-project behavior belongs in a skill; project-specific behavior belongs in `AGENTS.md`. |
| Architecture summary | Skill or `PROJECT_BRIEF.md` | Sometimes | Durable Hermes architecture belongs in a skill; project-specific architecture belongs in `PROJECT_BRIEF.md`. |
| Decision log | `docs/DECISIONS.md` | No | Keep durable decisions and reasons. Avoid turning it into a diary. |
| Risk register | `docs/RISKS.md` | Sometimes | Active risk summaries may be read during startup; details stay in the risk doc. |
| Permission matrix | `docs/RISKS.md` | Sometimes | Map to confirmation levels and high-risk action rules. |
| Changelog | `docs/project-log/` | Latest only | Codex reads only the latest entry by default. |
| Meeting notes | `docs/project-log/` or archive | Latest only | Summarize decisions and follow-ups; do not dump raw transcripts into startup files. |
| Source/content policy | `docs/SOURCE_POLICY.md` | As needed | Use when the project ingests, summarizes, republishes, downloads, or mirrors content. |
| Glossary or domain terms | `docs/TERMS.md` | As needed | Use when domain vocabulary affects output quality or safety. |
| Runbook for live operations | `docs/RISKS.md` plus project docs | No by default | Keep dangerous runtime actions behind explicit confirmation. |
| Old screenshots/reports | Archive outside startup path | No | Link only sanitized summaries if they still matter. |

## How To Collapse Overlapping Docs

When several old files say similar things, use this rule:

- **Current truth** goes to `PROJECT_BRIEF.md`.
- **Current work** goes to `WORKPLAN.md`.
- **Why we chose something** goes to `docs/DECISIONS.md`.
- **What can go wrong** goes to `docs/RISKS.md`.
- **What happened previously** goes to `docs/project-log/`.

If a fact appears in more than one place, pick the canonical destination and delete or archive the duplicate.

## Examples

### Project Continuity Brief

Old sections often map like this:

- "Where we are now" -> `PROJECT_BRIEF.md` / `One-Line State`
- "What exists" -> `PROJECT_BRIEF.md` / `Current Capabilities`
- "Open work" -> `WORKPLAN.md` / `Active Tasks`
- "Known risks" -> `docs/RISKS.md`
- "Past milestones" -> `docs/project-log/`

### Project Status

Old status files often mix active work and history.

Split them:

- incomplete tasks -> `WORKPLAN.md`;
- done items -> latest `docs/project-log/YYYY-MM-DD.md`;
- decisions made while completing work -> `docs/DECISIONS.md`;
- follow-up risk -> `docs/RISKS.md`.

### Permission Or Safety Notes

Map operational safety notes into `docs/RISKS.md`:

- Low: reads, drafts, local analysis, non-destructive checks;
- Medium: local file generation, local scripts, local commit;
- High: credentials, runtime config, external writes, deletes, push, publish, deploy, service restart.

High-risk actions require explicit confirmation.

## Archive Policy

After migration, keep old docs only when they still provide value.

Recommended archive pattern:

```text
docs/archive/YYYY-MM-DD-legacy-docs/
```

Before archiving, remove credentials, private paths, raw chat logs, customer data, and generated reports containing private content.
