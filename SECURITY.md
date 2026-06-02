# Security Policy

This project is a public operating-pattern starter kit. It should not contain real credentials, runtime profiles, memories, sessions, customer data, or private project material.

## Sensitive Material

Never commit:

- `.env` files or API keys;
- messaging-platform app secrets;
- Hermes profile directories;
- memory/session databases;
- Kanban SQLite databases;
- local browser profiles or cookies;
- generated reports containing private source material.

## Runtime Actions

The framework treats these as high-risk and requiring explicit user confirmation:

- external writes or sends;
- credential or allowlist changes;
- gateway/profile/config/memory edits;
- service restarts;
- deletes, migrations, pushes, publishes, or deployments.

## Reporting

For a public repo, use GitHub private vulnerability reporting if enabled. Otherwise open a minimal issue that does not include secrets or private data.

