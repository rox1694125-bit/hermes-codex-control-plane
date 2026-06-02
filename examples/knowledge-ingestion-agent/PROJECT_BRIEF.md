# PROJECT_BRIEF

Updated: 2026-06-02

## One-Line State

This sample project demonstrates a messaging-triggered knowledge ingestion workflow using the Hermes-Codex 3+3 project standard.

## Canonical Paths

- Project path: `examples/knowledge-ingestion-agent`
- Runtime profile: `example-knowledge-ingestion`
- Knowledge root: `knowledge/`
- Reports: `reports/`

## Scope

In scope:

- ingesting user-provided article URLs;
- producing local Markdown notes;
- extracting candidate concepts;
- building local indexes;
- mirroring summaries to a messaging workspace after explicit confirmation.

Out of scope unless reopened:

- bypassing platform access control;
- storing credentials in the repository;
- automatically publishing content externally;
- deleting source material.

## Current Capabilities

- Project standard files exist.
- Ingestion scripts are planned but not implemented.
- Messaging integration is planned as a runtime concern, not a Codex control surface.

## Current Next Steps

See `WORKPLAN.md`.

## Risk Summary

Runtime writes, credential changes, gateway changes, and deletion require explicit confirmation. See `docs/RISKS.md`.

