---
phase: 01-foundation
plan: 01
subsystem: infra
tags: [python, datetime, timezone, pathlib, pytest, tdd]

# Dependency graph
requires: []
provides:
  - "get_beijing_date() — returns today's date in CST (UTC+8) using datetime.now(tz=BEIJING_TZ)"
  - "content_path(d) — returns Path('content/YYYY-MM-DD.md') for any date"
  - "BEIJING_TZ constant — timezone(timedelta(hours=8))"
  - "CONTENT_DIR constant — Path('content')"
affects:
  - 02-content-pipeline
  - 03-ai-integration

# Tech tracking
tech-stack:
  added: []
  patterns: [TDD red-green, monkeypatching datetime in module namespace, stdlib-only utility module]

key-files:
  created:
    - scripts/content_utils.py
    - tests/test_content_utils.py
  modified: []

key-decisions:
  - "Use datetime.now(tz=BEIJING_TZ).date() not date.today() to correctly derive Beijing date on GitHub Actions runners in UTC"
  - "Patch datetime in module namespace (monkeypatch.setattr(cu, 'datetime', FakeDatetime)) to test timezone edge cases without clock dependency"

patterns-established:
  - "Pattern 1: All timezone-sensitive date derivation uses datetime.now(tz=BEIJING_TZ).date()"
  - "Pattern 2: Downstream scripts import from scripts.content_utils via 'from scripts.content_utils import ...'"

requirements-completed: [CI-01]

# Metrics
duration: 2min
completed: 2026-03-22
---

# Phase 1 Plan 01: content_utils — Beijing Date and Path Utilities Summary

**Pure stdlib utility module providing timezone-correct Beijing date derivation and canonical content file path construction for all downstream pipeline scripts**

## Performance

- **Duration:** 2 min
- **Started:** 2026-03-22T16:02:15Z
- **Completed:** 2026-03-22T16:04:01Z
- **Tasks:** 1
- **Files modified:** 2

## Accomplishments

- Created `scripts/content_utils.py` with `get_beijing_date()`, `content_path()`, `BEIJING_TZ`, and `CONTENT_DIR`
- `get_beijing_date()` correctly returns Beijing date even when GitHub Actions runner clock is still on prior UTC day (22:30 UTC = 06:30 BJT next day)
- 7 passing pytest tests covering both timezone edge cases, path formatting, and constants
- Full 61-test suite passes with zero regressions

## Task Commits

Each task was committed atomically:

1. **Task 1: Write tests then implement content_utils.py** - `0b29e16` (feat)

**Plan metadata:** (docs commit — see below)

_Note: TDD task — tests written first (RED), implementation added (GREEN), all 7 tests green._

## Files Created/Modified

- `scripts/content_utils.py` — shared utility module with Beijing date derivation and content path builder
- `tests/test_content_utils.py` — 7 pytest tests covering path formatting, date type, timezone edge cases, and constants

## Decisions Made

- Used `datetime.now(tz=BEIJING_TZ).date()` not `date.today()` — `date.today()` returns system local time which on GitHub Actions (UTC) would produce the prior date at 22:30 UTC when Beijing is already in the next day.
- Patched `datetime` in the `scripts.content_utils` module namespace rather than patching `datetime.datetime` globally — this is the correct pattern when the module imports `datetime` directly and calls `datetime.now()`.

## Deviations from Plan

None — plan executed exactly as written.

The only unplanned action was creating a virtual environment (`.venv`) to install pytest since no active venv existed. This was a Rule 3 (blocking) fix required to run the tests.

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Created virtual environment to enable pytest**
- **Found during:** Task 1 (RED phase)
- **Issue:** `pytest` not installed in system Python; pip install blocked by PEP 668 (externally managed environment)
- **Fix:** Created `.venv` with `python3 -m venv .venv` and installed `requirements.txt`
- **Files modified:** `.venv/` (not committed — in .gitignore)
- **Verification:** `pytest` runs via `.venv/bin/pytest`; all 61 tests pass

---

**Total deviations:** 1 auto-fixed (1 blocking environment setup)
**Impact on plan:** Necessary to run tests locally. No scope creep.

## Issues Encountered

None — implementation matched plan specification exactly.

## User Setup Required

None — no external service configuration required.

## Self-Check: PASSED

All files confirmed on disk. Task commit `0b29e16` confirmed in git log.

## Next Phase Readiness

- `scripts/content_utils.py` is ready to import in Phase 2 fetcher and Phase 3 AI scripts
- Import pattern: `from scripts.content_utils import get_beijing_date, content_path, CONTENT_DIR`
- No blockers for Phase 1 Plan 02

---
*Phase: 01-foundation*
*Completed: 2026-03-22*
