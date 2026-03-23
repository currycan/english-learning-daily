---
phase: 07-custom-endpoint-implementation
plan: 02
subsystem: api
tags: [anthropic, custom-endpoint, base-url, auth-token, env-vars, tdd]

# Dependency graph
requires:
  - phase: 07-01
    provides: "Three failing tests (TPROV-01, TPROV-02, TPROV-03, CONF-01-03, TEST-01-02) defining the custom endpoint contract"
provides:
  - "Extended call_claude() accepting base_url and auth_token optional params with env var priority chain"
  - "Conditional kwargs pattern — empty values never passed to Anthropic() SDK"
  - "Updated _dispatch() forwarding anthropic_base_url and anthropic_auth_token from model_config"
  - "Extended model_config in generate_exercises.py with anthropic_base_url and anthropic_auth_token keys"
affects: [08-custom-endpoint-docs]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Env var priority chain: os.environ.get('ANTHROPIC_BASE_URL') or kwarg or empty"
    - "Conditional SDK kwargs dict — only populate when non-empty to preserve SDK defaults"
    - "Config key forwarding: config.get() -> model_config dict -> _dispatch() -> call_claude() kwargs"

key-files:
  created: []
  modified:
    - scripts/ai_provider.py
    - scripts/generate_exercises.py

key-decisions:
  - "Conditional kwargs dict pattern — kwargs[key] set only when non-empty; avoids overriding SDK defaults with None or empty string"
  - "os.environ.get() or kwarg or '' chain handles GitHub Actions empty-string secret behavior"
  - "model_config.get() used (not []) to maintain backward compat with tests passing openai-only model_config"

patterns-established:
  - "env-var-priority: ANTHROPIC_BASE_URL > base_url kwarg > SDK default; same for AUTH_TOKEN"
  - "conditional-sdk-kwargs: build a kwargs dict, populate only non-empty fields, pass as **kwargs"

requirements-completed: [TPROV-01, TPROV-02, TPROV-03, TPROV-04, CONF-01, CONF-02, CONF-03]

# Metrics
duration: 10min
completed: 2026-03-23
---

# Phase 7 Plan 02: Custom Endpoint Implementation Summary

**call_claude() extended with env var priority chain (ANTHROPIC_BASE_URL/ANTHROPIC_AUTH_TOKEN > kwargs > SDK defaults) using conditional kwargs dict, wired through _dispatch() and generate_exercises.py model_config**

## Performance

- **Duration:** ~10 min
- **Started:** 2026-03-23T06:20:00Z
- **Completed:** 2026-03-23T06:30:00Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- Extended call_claude() with base_url and auth_token params, env var priority chain, and conditional kwargs pattern
- Updated _dispatch() to pass anthropic_base_url/anthropic_auth_token from model_config to call_claude()
- Extended model_config dict in generate_exercises.py main() to include both anthropic config.json fields
- All 118 tests pass including the 3 new custom endpoint tests from Plan 01 (TDD GREEN phase complete)

## Task Commits

Each task was committed atomically:

1. **Task 1: Extend call_claude() and _dispatch() in ai_provider.py** - `d5d542c` (feat)
2. **Task 2: Extend model_config in generate_exercises.py** - `8f2a9fd` (feat)

**Plan metadata:** TBD (docs: complete plan)

## Files Created/Modified

- `scripts/ai_provider.py` - Extended call_claude() signature with base_url/auth_token params; env var priority resolution; conditional Anthropic() kwargs; updated _dispatch() to forward model_config anthropic keys
- `scripts/generate_exercises.py` - Extended model_config dict in main() with anthropic_base_url and anthropic_auth_token keys sourced via config.get()

## Decisions Made

- Conditional kwargs dict: build empty dict, set key only when effective value is non-empty — avoids passing None or "" to the Anthropic SDK which would override SDK defaults
- `os.environ.get("ANTHROPIC_BASE_URL") or base_url or ""` chain: `or` operator treats both None and empty string as falsy, naturally handling GitHub Actions returning "" for unset secrets
- Used `.get()` (not `[]`) for model_config anthropic keys in _dispatch() to maintain backward compatibility with existing tests that pass openai-only model_config dicts

## Deviations from Plan

None — plan executed exactly as written.

## Issues Encountered

- venv discovery needed: neither `pytest` nor `python` were on PATH; found correct venv at `/Users/andrew/study-all/venv/bin/pytest` (the `.venv/` dir lacked the anthropic package)

## User Setup Required

None — no external service configuration required. Existing ANTHROPIC_API_KEY secret continues to work. New ANTHROPIC_BASE_URL and ANTHROPIC_AUTH_TOKEN secrets are optional and only applied when set.

## Next Phase Readiness

- All TPROV and CONF requirements fulfilled (TPROV-01 through TPROV-04, CONF-01 through CONF-03)
- Phase 8 (docs) can now document the stable custom endpoint interface
- GitHub Actions workflow changes (CONF-03 env block) documented for Phase 8 if not already handled

---
*Phase: 07-custom-endpoint-implementation*
*Completed: 2026-03-23*
