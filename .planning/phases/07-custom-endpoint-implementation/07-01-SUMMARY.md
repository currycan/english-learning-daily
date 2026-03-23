---
phase: 07-custom-endpoint-implementation
plan: 01
subsystem: testing
tags: [pytest, tdd, anthropic, custom-endpoint, monkeypatch]

# Dependency graph
requires:
  - phase: 06-openai-docs
    provides: existing test_ai_provider.py patterns and call_claude() implementation

provides:
  - Three failing TDD RED tests in tests/test_ai_provider.py defining behavioral contract for call_claude() custom endpoint support

affects:
  - 07-02-PLAN.md (GREEN phase: implements call_claude() to satisfy these tests)

# Tech tracking
tech-stack:
  added: []
  patterns: [monkeypatch.setenv/delenv for env var isolation in pytest, patch("scripts.ai_provider.anthropic.Anthropic") + MockAnthropic.assert_called_once_with() for constructor argument verification]

key-files:
  created: []
  modified:
    - tests/test_ai_provider.py

key-decisions:
  - "Backward compat test (test_call_claude_backward_compat_no_custom_config) passes immediately — correct behavior since current Anthropic() with no args already matches the no-env-var contract; RED state confirmed by other two tests failing"
  - "Test 3 uses base_url kwarg directly on call_claude() to represent config.json code path, not a separate env var"

patterns-established:
  - "Custom endpoint tests: monkeypatch.setenv/delenv to control ANTHROPIC_BASE_URL and ANTHROPIC_AUTH_TOKEN, then assert MockAnthropic called with expected kwargs"

requirements-completed:
  - TPROV-01
  - TPROV-02
  - TPROV-03
  - CONF-01
  - CONF-02
  - CONF-03
  - TEST-01
  - TEST-02

# Metrics
duration: 4min
completed: 2026-03-23
---

# Phase 7 Plan 01: TDD RED — Three Failing Tests for Custom Endpoint Behavior

**Three pytest tests that define the full behavioral contract for call_claude() custom base_url and auth_token support, using monkeypatch + MockAnthropic.assert_called_once_with() assertions**

## Performance

- **Duration:** ~4 min
- **Started:** 2026-03-23T06:18:27Z
- **Completed:** 2026-03-23T06:22:00Z
- **Tasks:** 1
- **Files modified:** 1

## Accomplishments

- Added three test functions to `tests/test_ai_provider.py` covering all TPROV and CONF requirements
- Confirmed RED state: 2 tests fail (TypeError / AssertionError), 1 test correctly passes (backward compat)
- All 17 pre-existing tests remain green (verified with `pytest -k "not (...)"`)

## Task Commits

1. **Task 1: Write three failing tests for custom endpoint behavior (RED)** - `2529f45` (test)

**Plan metadata:** (docs commit follows)

## Files Created/Modified

- `tests/test_ai_provider.py` - Appended new section with 3 test functions and section comment block

## Decisions Made

- The backward compatibility test (`test_call_claude_backward_compat_no_custom_config`) passes immediately because the current `call_claude()` already calls `anthropic.Anthropic()` with no arguments — this is intentional and correct. The RED requirement is satisfied by the other two tests failing. The plan's warning "if any test passes, the test is wrong" referred to tests incorrectly asserting future behavior; test 2 correctly captures already-correct behavior.
- Test 3 passes `base_url` as a direct kwarg to `call_claude()` to represent the config.json fallback path (CONF-03). This will require Plan 02 to add `base_url` as a parameter to `call_claude()`.

## Deviations from Plan

None - plan executed exactly as written. The three test functions were appended verbatim from the plan's `<action>` block.

## Issues Encountered

- `pytest` command not on PATH; needed `source venv/bin/activate` first (correct venv is `venv/` not `.venv/`)

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Three tests define the exact behavioral contract for Plan 02 (GREEN phase)
- Plan 02 must: add `base_url` and `auth_token` parameters to `call_claude()`, read `ANTHROPIC_BASE_URL` / `ANTHROPIC_AUTH_TOKEN` env vars, pass them to `anthropic.Anthropic()` constructor
- All existing tests green and ready for implementation

---
*Phase: 07-custom-endpoint-implementation*
*Completed: 2026-03-23*
