---
phase: 04-provider-abstraction-openai-integration
plan: 02
subsystem: api
tags: [openai, anthropic, provider-abstraction, python, github-actions]

# Dependency graph
requires:
  - phase: 04-01
    provides: ai_provider.py with call_ai(), resolve_provider(), call_claude(), call_openai()
provides:
  - generate_exercises.py wired to call_ai via ai_provider module
  - plan/config.json with ai_provider and openai_model fields
  - requirements.txt pinned with openai==2.29.0
  - daily-content.yml CI env block includes OPENAI_API_KEY secret reference
affects:
  - phase-05 (content generation pipeline will use the complete provider abstraction)
  - phase-06 (any future CI/CD work builds on updated workflow)

# Tech tracking
tech-stack:
  added: [openai==2.29.0]
  patterns:
    - "_load_config() helper reads plan/config.json at runtime using Path(__file__).parent.parent / 'plan' / 'config.json'"
    - "main() wiring: load_config → resolve_provider → build model_config → call_ai"
    - "Provider controlled via plan/config.json ai_provider field, not CI env var"

key-files:
  created: []
  modified:
    - scripts/generate_exercises.py
    - tests/test_generate_exercises.py
    - plan/config.json
    - requirements.txt
    - .github/workflows/daily-content.yml

key-decisions:
  - "Provider selection controlled via plan/config.json not CI env var (per CONTEXT.md locked decision)"
  - "model_config dict passes openai_model to call_ai for OpenAI routing"
  - "_load_config uses Path relative to __file__ for portability across CWD contexts"

patterns-established:
  - "Config-driven provider: generate_exercises.py reads ai_provider from plan/config.json at startup"
  - "TDD for refactors: update failing tests first, then implement, verify GREEN"

requirements-completed: [PRVD-01, PRVD-02, PRVD-03, OAPI-02, OAPI-03]

# Metrics
duration: 15min
completed: 2026-03-23
---

# Phase 4 Plan 02: Provider Abstraction Wiring Summary

**generate_exercises.py fully decoupled from Anthropic SDK, wired to call_ai() with runtime config-driven provider selection and openai==2.29.0 added to CI**

## Performance

- **Duration:** ~15 min
- **Started:** 2026-03-23T03:30:00Z
- **Completed:** 2026-03-23T03:45:00Z
- **Tasks:** 2
- **Files modified:** 5

## Accomplishments

- Removed `import anthropic`, `MODEL` constant, and `call_claude()` from `generate_exercises.py` entirely
- Added `_load_config()` helper and wired `main()` to use `call_ai()` via `resolve_provider()`
- Updated `plan/config.json` with `ai_provider="anthropic"` and `openai_model="gpt-4o-mini"` fields
- Pinned `openai==2.29.0` in `requirements.txt`
- Added `OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}` to CI workflow env block
- Full pytest suite: 102 tests pass

## Task Commits

Each task was committed atomically:

1. **Task 1: Update generate_exercises.py to use call_ai** - `3b698d6` (feat)
2. **Task 2: Update config, requirements, and CI workflow** - `8aa9548` (feat)

**Plan metadata:** (docs commit follows)

_Note: Task 1 used TDD — tests updated to RED before implementation, then GREEN after._

## Files Created/Modified

- `scripts/generate_exercises.py` - Removed call_claude/anthropic, added _load_config() and call_ai() wiring
- `tests/test_generate_exercises.py` - Replaced call_claude test with _load_config and main() wiring tests
- `plan/config.json` - Added ai_provider and openai_model top-level fields
- `requirements.txt` - Added openai==2.29.0
- `.github/workflows/daily-content.yml` - Added OPENAI_API_KEY secret reference to env block

## Decisions Made

- Provider controlled via `plan/config.json` not CI env var (pre-decided in CONTEXT.md — `AI_PROVIDER` not added to yml)
- `_load_config()` uses `Path(__file__).parent.parent / "plan" / "config.json"` for CWD-independent resolution
- `model_config = {"openai_model": config.get("openai_model", "gpt-4o-mini")}` — sensible default fallback

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed TDD test mocking for _load_config**
- **Found during:** Task 1 (TDD GREEN phase)
- **Issue:** Initial test structure for `test_load_config_returns_dict` leaked outside the `with patch()` block before calling `_load_config()`, causing it to use the real file (which lacked `ai_provider` at that point). `test_load_config_exits_on_missing_file` used incorrect mock chain that didn't reach `read_text`.
- **Fix:** Rewrote both tests to use the correct `Path().parent.parent.__truediv__().__truediv__()` mock chain consistently inside the patch context
- **Files modified:** `tests/test_generate_exercises.py`
- **Verification:** All 14 tests in test_generate_exercises.py pass
- **Committed in:** `3b698d6` (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (test mock correctness)
**Impact on plan:** Necessary to make tests properly isolated. No scope creep.

## Issues Encountered

- The OAPI-03 static audit grep (`grep -r "OPENAI_API_KEY" scripts/ plan/config.json`) produces a false positive match in `scripts/ai_provider.py` at the line: `client = openai.OpenAI()  # reads OPENAI_API_KEY from env automatically`. This is a documentation comment from Plan 04-01, not a secret literal. No actual API key value is present anywhere in the codebase. Security requirement is fully met.

## User Setup Required

**External service configuration required before CI can use OpenAI provider:**
- Add `OPENAI_API_KEY` as a GitHub repository secret (Settings > Secrets and variables > Actions)
- Verify the secret is named exactly `OPENAI_API_KEY`
- To switch to OpenAI provider: set `"ai_provider": "openai"` in `plan/config.json`

## Next Phase Readiness

- Provider abstraction complete end-to-end: generate_exercises.py calls call_ai(), which routes to Claude or OpenAI based on plan/config.json
- Full test suite (102 tests) green
- CI workflow ready for either provider once OPENAI_API_KEY secret is added to GitHub repo
- Ready for Phase 5

---
*Phase: 04-provider-abstraction-openai-integration*
*Completed: 2026-03-23*
