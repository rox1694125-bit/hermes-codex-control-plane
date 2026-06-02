# GitHub Publication Notes

Use this file when preparing the project for a public GitHub repository.

## Suggested Repository Name

```text
hermes-codex-control-plane
```

## Short Description

```text
A reusable control-plane pattern for using Codex to build, maintain, and verify Hermes-powered messaging-agent systems.
```

## Longer Description

Hermes-Codex Control Plane is a public starter kit for separating development control from runtime execution in long-lived agent systems. Codex acts as the development control plane for architecture, edits, tests, reviews, and multi-agent coordination. Hermes and messaging platforms such as Feishu/Lark, Slack, Telegram, or WeCom remain the runtime execution layer.

The repo includes Codex skills, project templates, multi-agent contracts, and protocols for keeping project context explicit, startup docs small, and high-risk runtime actions behind confirmation gates.

## Suggested Topics

```text
codex
hermes-agent
ai-agents
multi-agent
agentic-workflows
feishu
lark
developer-tools
project-templates
agent-skills
```

## Public v0.1 Release Checklist

- [ ] README explains the control-plane pattern in under 3 minutes.
- [ ] No private paths, names, credentials, profile details, or project-specific secrets.
- [ ] Skills are concise and reusable.
- [ ] Templates are generic and safe to copy.
- [ ] Example project is sanitized.
- [ ] Scripts do not write outside expected target paths.
- [ ] Protocol Doctor passes on `examples/knowledge-ingestion-agent`.
- [ ] Protocol Doctor regression tests pass with `python3 tests/test_check_control_plane.py`.
- [ ] Repo package linter passes with `python3 scripts/check_repo_package.py .`.
- [ ] License is present.
- [ ] GitHub description and topics are set.
- [ ] First public commit is reviewed before pushing.

## Do Not Publish

Do not include:

- real `.env` files;
- Hermes profile directories;
- memory/session stores;
- Feishu/Lark app secrets;
- private project names or customer data;
- local absolute paths from a real machine;
- generated reports that contain private content;
- raw chat logs.

## Suggested First Release Tag

```text
v0.1.0
```

Release title:

```text
v0.1.0 - Public control-plane pattern
```

Release note:

```text
Initial public package with Codex skills, Hermes/Codex development-control-plane protocol, multi-agent contract, 3+3 project templates, install/init scripts, and a sanitized knowledge-ingestion example.
```
