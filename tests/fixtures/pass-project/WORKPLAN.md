# WORKPLAN

Updated: 2026-06-02

## Active Tasks

| ID | Task | Risk | Acceptance Criteria | Status |
|---|---|---|---|---|
| T001 | Keep fixture compliant | Low | Doctor exits 0 with no warnings | active |

## Test Scenarios

1. Doctor pass:
   - required files exist;
   - required sections exist;
   - safety scan has no findings.

## Required Checks

```bash
python3 scripts/check_control_plane.py .
```
