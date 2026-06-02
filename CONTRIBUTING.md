# Contributing

This project is an operating pattern, so contributions should improve clarity, safety, and reuse.

Good contributions:

- clearer project templates;
- better multi-agent contracts;
- sanitized examples;
- safer confirmation rules;
- concise skills that trigger correctly;
- migration guidance for existing projects.

Avoid:

- private paths, credentials, or user-specific instructions;
- long skill bodies that belong in docs;
- making live runtime changes automatic by default;
- adding many required project files without a clear model-startup benefit.

## Skill Guidelines

Skills should stay concise and task-triggerable.

- Put trigger conditions in `description`.
- Put only core workflow in `SKILL.md`.
- Put public explanation in `docs/`, not inside skills.
- Avoid private or organization-specific assumptions unless the skill is explicitly private.

## Template Guidelines

Templates should be useful when copied into a new project.

- Keep required startup files short.
- Use placeholders where user-specific values belong.
- Put optional domain docs behind clear conditions.

