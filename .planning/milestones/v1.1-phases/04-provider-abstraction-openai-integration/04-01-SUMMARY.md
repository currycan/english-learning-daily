---
phase: 04-provider-abstraction-openai-integration
plan: "01"
subsystem: ai-provider
tags: [tdd, openai, anthropic, provider-abstraction]
dependency_graph:
  requires: []
  provides: [scripts/ai_provider.py]
  affects: [scripts/generate_exercises.py]
tech_stack:
  added: [openai==2.29.0]
  patterns: [provider-dispatch, client-inside-function, env-var-priority]
key_files:
  created:
    - scripts/ai_provider.py
    - tests/test_ai_provider.py
  modified: []
decisions:
  - "CLAUDE_MODEL hardcoded in ai_provider.py, not in config — single source of truth for model version"
  - "call_claude catches anthropic.APIError specifically, not bare Exception — fixes v1.0 tech debt"
  - "openai.OpenAI() instantiated inside call_openai() for testability — mirrors existing anthropic pattern"
  - "openai pinned at 2.29.0, added to venv only (requirements.txt updated in Plan 02)"
metrics:
  duration: "134s"
  completed_date: "2026-03-23"
  tasks_completed: 2
  tasks_total: 2
  files_created: 2
  files_modified: 0
---

# Phase 4 Plan 1: AI Provider Abstraction Summary

**One-liner:** TDD-built `scripts/ai_provider.py` that routes Claude/OpenAI calls via `resolve_provider` + `call_ai` dispatcher, fixing bare-Exception tech debt from v1.0.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Write tests/test_ai_provider.py (RED phase) | e3f0891 | tests/test_ai_provider.py (+120 lines) |
| 2 | Create scripts/ai_provider.py (GREEN phase) | 5edf740 | scripts/ai_provider.py (+74 lines) |

## What Was Built

`scripts/ai_provider.py` exports:
- `VALID_PROVIDERS = {"anthropic", "openai"}` — module-level constant
- `CLAUDE_MODEL = "claude-haiku-4-5-20251001"` — hardcoded per CONTEXT.md decision
- `resolve_provider(config: dict) -> str` — env var `AI_PROVIDER` takes priority over config key
- `call_claude(prompt, max_tokens) -> str` — catches `anthropic.APIError` (not bare Exception)
- `call_openai(prompt, model, max_tokens) -> str` — instantiates `openai.OpenAI()` inside function
- `call_ai(prompt, provider, model_config, max_tokens) -> str` — dispatches to correct provider

`tests/test_ai_provider.py` has 11 tests covering all 6 behavioral categories. All pass with mocked API calls — no live requests.

## Success Criteria Verification

1. `scripts/ai_provider.py` exists and exports all required symbols — PASS
2. `tests/test_ai_provider.py` has 11 tests, all passing — PASS
3. `call_claude` catches `anthropic.APIError` (`grep: except anthropic.APIError`) — PASS
4. `CLAUDE_MODEL = "claude-haiku-4-5-20251001"` hardcoded in ai_provider.py — PASS
5. `openai.OpenAI()` instantiated inside `call_openai()`, not at module level — PASS
6. `pytest` exits 0 for full suite (100 tests) — PASS

## Deviations from Plan

None — plan executed exactly as written.

## Self-Check: PASSED

- `scripts/ai_provider.py` exists: FOUND
- `tests/test_ai_provider.py` exists: FOUND
- Commit e3f0891 exists: FOUND
- Commit 5edf740 exists: FOUND
- Full suite 100 tests passing: CONFIRMED
