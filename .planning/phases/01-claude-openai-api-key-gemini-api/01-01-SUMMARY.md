---
phase: 01-claude-openai-api-key-gemini-api
plan: 01
subsystem: ai-provider
tags: [gemini, migration, provider, ci]
dependency_graph:
  requires: []
  provides: [gemini-provider, call-gemini]
  affects: [scripts/ai_provider.py, scripts/generate_exercises.py, plan/config.json, .github/workflows/daily-content.yml]
tech_stack:
  added: [google-genai==1.68.0]
  removed: [anthropic==0.86.0, openai==2.29.0]
  patterns: [single-provider, env-var-priority, ProviderError-exception]
key_files:
  created: []
  modified:
    - requirements.txt
    - scripts/ai_provider.py
    - scripts/generate_exercises.py
    - plan/config.json
    - .github/workflows/daily-content.yml
    - tests/test_ai_provider.py
    - tests/test_ai_provider_docs.py
    - tests/test_generate_exercises.py
    - docs/ai-providers.md
decisions:
  - "Removed all Anthropic and OpenAI SDK code; single call_gemini() function with GEMINI_MODEL constant"
  - "GEMINI_API_KEY env var takes priority over api_key kwarg (mirrors old pattern)"
  - "ProviderError exception retained for consistent error handling pattern"
  - "docs/ai-providers.md rewritten for Gemini-only setup"
metrics:
  duration_minutes: 8
  completed_date: "2026-03-24"
  tasks_completed: 2
  files_changed: 9
---

# Phase 01 Plan 01: Replace AI Providers with Gemini-Only Summary

**One-liner:** Migrated from dual-provider (Anthropic + OpenAI) to single Gemini provider using google-genai SDK, replacing call_ai/resolve_provider with call_gemini() across all production code, config, and CI.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Replace dependencies and rewrite ai_provider.py to Gemini-only | 86f18ac | requirements.txt, scripts/ai_provider.py |
| 2 | Wire generate_exercises.py to call_gemini and update config + CI | 9251d65 | scripts/generate_exercises.py, plan/config.json, .github/workflows/daily-content.yml |

## Verification Results

All plan verification checks pass:

- `python3 -c "from scripts.ai_provider import call_gemini, ProviderError, GEMINI_MODEL"` exits 0
- `grep -r "anthropic|openai|call_ai|call_claude|resolve_provider" scripts/ --include="*.py"` returns no matches
- `grep -r "ANTHROPIC|OPENAI" .github/workflows/` returns no matches
- `config.json` contains `gemini_model`, no `ai_provider`, `openai_model`, or `claude_model`
- Full test suite: 114 passed, 1 warning

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Updated tests and docs for Gemini-only provider**

- **Found during:** Post-task verification (after Task 2 commit)
- **Issue:** `tests/test_ai_provider.py` tested `call_claude`, `call_openai`, `call_ai`, `resolve_provider` — all removed in Task 1. `tests/test_generate_exercises.py::test_main_calls_call_ai` patched the now-removed `call_ai`/`resolve_provider`. `tests/test_ai_provider_docs.py` asserted on Anthropic/OpenAI doc content. `docs/ai-providers.md` described the old dual-provider system.
- **Fix:** Rewrote `test_ai_provider.py` with 14 tests covering `call_gemini()` behavior, API key priority, model override, error handling, and absence of old functions. Updated `test_generate_exercises.py::test_main_calls_call_gemini` and `test_load_config_returns_dict`. Rewrote `test_ai_provider_docs.py` to assert Gemini doc content. Rewrote `docs/ai-providers.md` as Gemini-only setup guide.
- **Files modified:** tests/test_ai_provider.py, tests/test_ai_provider_docs.py, tests/test_generate_exercises.py, docs/ai-providers.md
- **Commit:** 7eb427b

## Known Stubs

None — all data paths are fully wired.

## Self-Check: PASSED

- scripts/ai_provider.py: EXISTS
- scripts/generate_exercises.py: EXISTS
- plan/config.json: EXISTS
- .github/workflows/daily-content.yml: EXISTS
- requirements.txt: EXISTS
- Commits 86f18ac, 9251d65, 7eb427b: FOUND
- 114/114 tests pass
