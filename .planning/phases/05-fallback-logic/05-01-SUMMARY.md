---
phase: 05-fallback-logic
plan: 01
subsystem: ai-provider
tags: [fallback, error-handling, tdd, provider-abstraction]
dependency_graph:
  requires: [04-02]
  provides: [FALL-01, FALL-02, FALL-03, TEST-02]
  affects: [scripts/ai_provider.py, tests/test_ai_provider.py]
tech_stack:
  added: []
  patterns: [ProviderError exception, try/except fallback chain, stderr logging, _dispatch helper]
key_files:
  created: []
  modified:
    - tests/test_ai_provider.py
    - scripts/ai_provider.py
decisions:
  - "ProviderError raised from call_claude/call_openai instead of sys.exit(1) — keeps low-level callers composable"
  - "_backup_provider uses set difference on VALID_PROVIDERS — deterministic with exactly two providers"
  - "_dispatch private helper avoids code duplication between primary and fallback paths in call_ai"
  - "openai.OpenAIError not used — bare Exception catch in call_openai is correct (wider net, consistent with prior Phase 4 decision)"
metrics:
  duration_seconds: 115
  completed_date: "2026-03-23"
  tasks_completed: 2
  files_modified: 2
---

# Phase 5 Plan 01: Provider Fallback Logic Summary

**One-liner:** ProviderError exception with automatic single-retry fallback via _dispatch helper — primary outage retries backup, both-fail exits 1 to stderr.

## Tasks Completed

| Task | Description | Commit | Phase |
|------|-------------|--------|-------|
| 1 | Write failing test stubs (RED) | acb69b5 | TDD RED |
| 2 | Implement fallback logic in ai_provider.py (GREEN) | 23ba05f | TDD GREEN |

## Files Modified

**tests/test_ai_provider.py**
- Renamed `test_call_claude_exits_on_api_error` → `test_call_claude_raises_provider_error_on_api_error`
- Renamed `test_call_openai_exits_on_error` → `test_call_openai_raises_provider_error_on_error`
- Both renamed tests now assert `pytest.raises(ap.ProviderError)` instead of `SystemExit`
- Added 6 new fallback tests covering FALL-01, FALL-02, FALL-03, TEST-02

**scripts/ai_provider.py**
- Updated docstring to reflect Phase 5 fallback behaviour
- Added `class ProviderError(Exception)` at module level
- `call_claude`: `sys.exit(1)` replaced with `raise ProviderError(...) from e`
- `call_openai`: `sys.exit(1)` replaced with `raise ProviderError(...) from e`
- Added `_backup_provider(primary: str) -> str` using set difference
- Added `_dispatch(prompt, provider, model_config, max_tokens)` private router
- `call_ai`: now catches `ProviderError`, logs WARNING to stderr, retries backup via `_dispatch`, logs ERROR and calls `sys.exit(1)` only when backup also fails

## Test Count

- Before: 11 tests (all passing)
- After: 17 tests (all passing, 108 total suite passing)

## Key Decisions Made

1. **ProviderError over sys.exit in low-level callers** — `call_claude` and `call_openai` now raise `ProviderError` instead of exiting directly. This makes them composable and testable without mocking sys.exit.

2. **_backup_provider via set difference** — `(VALID_PROVIDERS - {primary}).pop()` is deterministic with exactly two providers. No if/else needed.

3. **_dispatch private helper** — Avoids duplicating the provider-routing logic between the primary and fallback paths in `call_ai`.

4. **bare Exception in call_openai** — The plan specified this (consistent with Phase 4 decision). `openai.OpenAIError` was considered but bare Exception provides a wider net appropriate for this use case.

5. **generate_exercises.py unchanged** — `call_ai()` interface is fully backward-compatible. No callers needed updating.

## Deviations from Plan

None — plan executed exactly as written. The venv at `venv/` (not `.venv/`) was used since `.venv/` lacked the `anthropic` module.

## Phase Gate Verification

```
pytest tests/test_ai_provider.py -v  → 17/17 passed
pytest                               → 108/108 passed
python -c "from scripts.ai_provider import ProviderError, _backup_provider; assert _backup_provider('anthropic') == 'openai'; print('OK')"  → OK
grep "file=sys.stderr" scripts/ai_provider.py  → 3 matches (resolve_provider, call_ai WARNING, call_ai ERROR)
sys.exit only in resolve_provider (line 38) and call_ai (line 120) — not in call_claude or call_openai
```
