# WORKPLAN

Updated: 2026-06-02

## Working Rules

- Define smoke tests before implementing ingestion.
- Use multi-agent implementation only after file ownership and acceptance criteria are clear.
- Keep runtime profile/gateway changes behind explicit confirmation.

## Active Tasks

| ID | Task | Risk | Acceptance Criteria | Status |
|---|---|---|---|---|
| T001 | Implement local article ingestion smoke | Medium | Given a local raw text file, create a main note, raw note, concept candidates, and updated index | pending |
| T002 | Add read-only messaging command design | Low | Design doc explains URL intake, status reply, and failure modes without changing runtime config | pending |
| T003 | Add external mirror dry-run | Medium | Dry-run report shows what would be written without making external API calls | pending |

## Test Scenarios

1. Local article smoke:
   - input is a local raw text file;
   - output includes stable filenames;
   - index updates deterministically.

2. Unsupported source:
   - input URL cannot be accessed;
   - project writes a report or inbox item;
   - no hallucinated summary is produced.

3. External mirror dry-run:
   - no external write happens;
   - report lists intended target, payload summary, and recovery state.

## Required Checks

```bash
python3 scripts/check_project.py
python3 scripts/build_indexes.py --check
```

These scripts are examples; implement them in the sample if the project becomes executable.

