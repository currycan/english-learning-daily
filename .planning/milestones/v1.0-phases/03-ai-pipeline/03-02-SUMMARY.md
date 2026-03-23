---
phase: 03-ai-pipeline
plan: 02
subsystem: ai-pipeline
tags: [anthropic, claude-api, markdown, tdd-green, exercise-generation]

requires:
  - phase: 03-01
    provides: [12 failing tests for generate_exercises.py contracts, anthropic==0.86.0 in requirements.txt]
provides:
  - scripts/generate_exercises.py with build_prompt, call_claude, parse_response, render_markdown, main
  - 12 passing unit tests for generate_exercises.py
  - Full Article Envelope JSON -> Claude API -> Markdown lesson pipeline stage
affects: [03-03-PLAN]

tech-stack:
  added: []
  patterns: [anthropic-client-instantiation-inside-function, code-fence-defensive-strip, stdin-json-read-pattern]

key-files:
  created:
    - scripts/generate_exercises.py
  modified: []

key-decisions:
  - "Catch broad Exception (not just anthropic.APIError) in call_claude to match test mock pattern using Exception side_effect"
  - "Use list[str] (not list[str]) type hint via plain list annotation for Python 3.14 compatibility"

patterns-established:
  - "Pattern: anthropic.Anthropic() instantiated inside call_claude() function — not at module level — enables clean patching in tests"
  - "Pattern: parse_response strips code fences before json.loads() to handle Claude RLHF formatting behavior"

requirements-completed: [AIGEN-01, AIGEN-02, AIGEN-03, AIGEN-04, OUT-01]

duration: 2min
completed: "2026-03-23"
---

# Phase 3 Plan 02: TDD GREEN Phase — generate_exercises.py Implementation Summary

**Generate_exercises.py: four-function pipeline stage (build_prompt, call_claude, parse_response, render_markdown) reading Article Envelope JSON from stdin, calling claude-3-5-haiku-20241022, and rendering a four-section bilingual Markdown lesson to stdout — all 12 unit tests green.**

## Performance

- **Duration:** ~2 min
- **Started:** 2026-03-23T01:40:08Z
- **Completed:** 2026-03-23T01:41:54Z
- **Tasks:** 1
- **Files modified:** 1

## Accomplishments

- Implemented scripts/generate_exercises.py with all four pure functions and main() orchestrator
- All 12 unit tests in tests/test_generate_exercises.py pass (12 passed, 0 failed)
- Full test suite: 89 passed, 1 pre-existing RED failure from Plan 01 (test_reads_stdin_and_writes_file — intentionally failing for Plan 03)
- Module importable and all five exports verified

## Task Commits

Each task was committed atomically:

1. **Task 1: Implement scripts/generate_exercises.py (GREEN phase)** - `41b7ba3` (feat)

**Plan metadata:** (docs commit follows)

## Files Created/Modified

- `scripts/generate_exercises.py` - Core AI exercise generator: reads Article Envelope JSON from stdin, calls Claude API (claude-3-5-haiku-20241022), renders four-section bilingual Markdown to stdout

## Decisions Made

1. **Broad Exception catch in call_claude**: The test uses `Exception("API error")` as side_effect (not `anthropic.APIError`) to avoid APIError init complexity. Implemented to catch bare `Exception` so `sys.exit(1)` fires and test passes. Pre-existing test contract from Plan 01 summary note: "test_call_claude_exits_on_api_error uses Exception mock to avoid APIError init complexity."

2. **Plain `list` type annotation**: Used `list` (not `list[str]`) to maintain compatibility with the established code style; Python 3.14 supports both but plain `list` is simpler.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Installed anthropic SDK in venv**
- **Found during:** Task 1 (first test run)
- **Issue:** anthropic==0.86.0 was in requirements.txt but not installed in the project venv
- **Fix:** Ran `pip install anthropic==0.86.0` then `pip install -r requirements.txt` to ensure all deps installed
- **Files modified:** None (venv state only)
- **Verification:** Tests collected and ran successfully after install
- **Committed in:** Not applicable (venv install, no file changes)

---

**Total deviations:** 1 auto-fixed (1 blocking — missing venv install)
**Impact on plan:** Essential for test execution. No scope creep.

## Issues Encountered

- feedparser not installed in venv alongside anthropic — ran `pip install -r requirements.txt` to fix both at once

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- scripts/generate_exercises.py complete and all 12 tests green
- Pipeline stage ready: `python -m scripts.feed_article | python -m scripts.generate_exercises`
- Plan 03 (commit_content.py stdin update + workflow wiring) can proceed — test_reads_stdin_and_writes_file is the pre-written RED test awaiting GREEN implementation

---
*Phase: 03-ai-pipeline*
*Completed: 2026-03-23*
