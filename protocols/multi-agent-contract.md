# Multi-Agent Contract

This protocol makes Codex subagents stable enough for Hermes + Feishu project development.

## When To Use Subagents

Use subagents after the planning/test contract is clear.

Good subagent work:

- read-only architecture exploration;
- independent implementation slices with disjoint write scopes;
- verification after implementation;
- risk review for high-blast-radius changes.

Avoid subagents when:

- the next local step is blocked on the answer;
- task scope is still vague;
- multiple workers would touch the same files;
- high-risk confirmation has not been obtained.

## Standard Roles

Explorer:

- read-only;
- answers concrete architecture or codebase questions;
- cites files and functions;
- does not edit.

Worker:

- edits a bounded file/module set;
- must know owned and forbidden files;
- must not revert unrelated changes;
- reports changed files and tests.

Verifier:

- reviews resulting changes;
- runs or designs checks;
- focuses on bugs, regressions, missing tests, and risk.

## Worker Prompt Template

```text
You are a worker in a shared codebase. Other agents or the user may be editing in parallel.

Task:
<specific implementation goal>

Owned files/modules:
<paths>

Do not touch:
<paths or areas>

Acceptance criteria:
<bullets>

Required checks:
<commands or scenarios>

Rules:
- Do not revert unrelated changes.
- Keep edits scoped.
- Follow existing project conventions.
- Final response must list changed files, checks run, and any blockers.
```

## Verifier Prompt Template

```text
You are a verifier. Review the current work for correctness and risk.

Focus:
<feature/change>

Evidence to inspect:
<files, tests, docs>

Check:
- behavior regressions
- missing tests
- project protocol violations
- high-risk actions needing confirmation

Do not edit unless explicitly asked. Final response should list findings by severity with file references.
```

