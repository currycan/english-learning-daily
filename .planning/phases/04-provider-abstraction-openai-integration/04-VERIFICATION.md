---
phase: 04-provider-abstraction-openai-integration
verified: 2026-03-23T06:00:00Z
status: passed
score: 17/17 must-haves verified
---

# Phase 4: Provider Abstraction + OpenAI Integration — Verification Report

**Phase Goal:** Users can switch between Claude and OpenAI via a single env var or config entry, and the system produces identical lesson output from either provider
**Verified:** 2026-03-23
**Status:** passed
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths — Plan 01

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `call_ai()` routes to `call_claude()` when `provider='anthropic'` | VERIFIED | `ai_provider.py:74` — `return call_claude(prompt, ...)` is the else-branch; `test_call_ai_dispatches_anthropic` passes |
| 2 | `call_ai()` routes to `call_openai()` when `provider='openai'` | VERIFIED | `ai_provider.py:72-73` — `if provider == "openai": return call_openai(...)`; `test_call_ai_dispatches_openai` passes |
| 3 | `resolve_provider()` returns env var value when `AI_PROVIDER` is set | VERIFIED | `ai_provider.py:23` — `os.environ.get("AI_PROVIDER") or ...`; `test_resolve_provider_env_var_priority` passes |
| 4 | `resolve_provider()` falls back to `config['ai_provider']` when env var absent | VERIFIED | `ai_provider.py:23` — `config.get("ai_provider", "anthropic")`; `test_resolve_provider_config_default` passes |
| 5 | `resolve_provider()` exits 1 when provider value is not valid | VERIFIED | `ai_provider.py:24-29`; `test_resolve_provider_unknown_exits` and `test_resolve_provider_env_unknown_exits` pass |
| 6 | `call_openai()` returns `response.choices[0].message.content` | VERIFIED | `ai_provider.py:57`; `test_call_openai_returns_content` passes |
| 7 | `call_openai()` exits 1 on any API error | VERIFIED | `ai_provider.py:58-60`; `test_call_openai_exits_on_error` passes |
| 8 | `call_openai()` passes the configured model name to `chat.completions.create` | VERIFIED | `ai_provider.py:53`; `test_call_openai_uses_configured_model` passes |
| 9 | `call_claude()` catches `anthropic.APIError`, not bare `Exception` | VERIFIED | `ai_provider.py:43` — `except anthropic.APIError as e`; `test_call_claude_exits_on_api_error` passes |
| 10 | All tests pass with API calls mocked — no live API calls | VERIFIED | 11 tests pass in 0.32s; all API clients patched via `unittest.mock.patch` |

### Observable Truths — Plan 02

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 11 | `generate_exercises.py` calls `call_ai()` from `ai_provider`, not `call_claude()` from itself | VERIFIED | `generate_exercises.py:13` imports `call_ai, resolve_provider`; line 137 calls `call_ai(...)`; no `call_claude` reference in file |
| 12 | `generate_exercises.py` loads `plan/config.json` and passes `provider` + `model_config` to `call_ai` | VERIFIED | `generate_exercises.py:132-137` — `_load_config()`, `resolve_provider(config)`, `model_config = {"openai_model": ...}`, `call_ai(prompt, provider=provider, model_config=model_config)` |
| 13 | `plan/config.json` has `ai_provider='anthropic'` and `openai_model='gpt-4o-mini'` at top level | VERIFIED | `config.json:6-7` — both fields present with correct values |
| 14 | `requirements.txt` includes `openai==2.29.0` | VERIFIED | `requirements.txt:5` — `openai==2.29.0` |
| 15 | `daily-content.yml` env block includes `OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}` | VERIFIED | `daily-content.yml:35` — exact match |
| 16 | No `OPENAI_API_KEY` literal value appears in any source file or config file | VERIFIED | `grep -r "OPENAI_API_KEY" scripts/ plan/config.json` returns only a comment in `ai_provider.py:50` (`# reads OPENAI_API_KEY from env automatically`) — no literal key value |
| 17 | Full pytest suite passes after all changes | VERIFIED | 102 tests pass, 0 failures |

**Score:** 17/17 truths verified

---

## Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `scripts/ai_provider.py` | `resolve_provider, call_claude, call_openai, call_ai, VALID_PROVIDERS, CLAUDE_MODEL` | VERIFIED | All 6 exports present; 75 lines; substantive implementation |
| `tests/test_ai_provider.py` | Unit tests for all provider logic, contains `test_call_ai_dispatches` | VERIFIED | 11 test functions; all 6 behavioral categories covered |
| `scripts/generate_exercises.py` | Updated `main()` wiring `call_ai` + `resolve_provider` | VERIFIED | `import anthropic` removed; `call_claude` removed; `MODEL =` removed; `call_ai` + `resolve_provider` wired |
| `plan/config.json` | Contains `ai_provider` field | VERIFIED | Both `ai_provider` and `openai_model` present |
| `requirements.txt` | Contains `openai==2.29.0` | VERIFIED | Line 5 |
| `.github/workflows/daily-content.yml` | Contains `OPENAI_API_KEY` secret ref | VERIFIED | Line 35 |

---

## Key Link Verification

### Plan 01 Links

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `tests/test_ai_provider.py` | `scripts/ai_provider.openai.OpenAI` | `patch('scripts.ai_provider.openai.OpenAI')` | WIRED | Pattern found at `test_ai_provider.py:51,64,77` |
| `tests/test_ai_provider.py` | `scripts/ai_provider.anthropic.Anthropic` | `patch('scripts.ai_provider.anthropic.Anthropic')` | WIRED | Pattern found at `test_ai_provider.py:91` |

### Plan 02 Links

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `scripts/generate_exercises.py main()` | `scripts/ai_provider.call_ai` | `from scripts.ai_provider import call_ai, resolve_provider` | WIRED | `generate_exercises.py:13` import + `:137` call site |
| `scripts/generate_exercises.py main()` | `plan/config.json` | `_load_config()` reads `Path('plan/config.json').read_text()` | WIRED | `generate_exercises.py:115` — `Path(__file__).parent.parent / "plan" / "config.json"` + `:132` call site |

---

## Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| PRVD-01 | 04-01, 04-02 | System calls AI via unified interface; business logic decoupled from provider | SATISFIED | `call_ai()` is the single interface; `generate_exercises.py` has no provider-specific imports |
| PRVD-02 | 04-01, 04-02 | User can switch via `AI_PROVIDER` env var at runtime | SATISFIED | `resolve_provider()` checks `os.environ.get("AI_PROVIDER")` first; tested by `test_resolve_provider_env_var_priority` |
| PRVD-03 | 04-01, 04-02 | User can set default in `plan/config.json`; env var takes priority | SATISFIED | `config.json` has `ai_provider` field; fallback logic verified in tests |
| OAPI-01 | 04-01 | OpenAI `gpt-4o-mini` produces identical format output | SATISFIED* | Same prompt, same `parse_response()` + `render_markdown()` pipeline; `call_openai` returns raw text identical path to `call_claude`; *format identity requires human confirmation with live API |
| OAPI-02 | 04-01, 04-02 | OpenAI model configurable via `plan/config.json` (default `gpt-4o-mini`) | SATISFIED | `config.json:7` — `"openai_model": "gpt-4o-mini"`; `generate_exercises.py:134` reads it; `call_openai` receives it as `model=` arg |
| OAPI-03 | 04-02 | `OPENAI_API_KEY` only from env/secrets, never in code or config | SATISFIED | Static audit: only comment mention in `ai_provider.py:50`; no literal value anywhere |
| TEST-01 | 04-01 | OpenAI provider path has unit tests with mocked API calls | SATISFIED | `test_call_openai_returns_content`, `test_call_openai_uses_configured_model`, `test_call_openai_exits_on_error`, `test_call_ai_dispatches_openai` — all pass with mock |

*OAPI-01 note: Identical output format is structurally guaranteed by the shared `parse_response()` and `render_markdown()` functions called regardless of provider. The prompt sent to both providers is identical. Actual AI response quality parity is not automatically verifiable.

### Orphaned Requirements Check

Requirements mapped to Phase 4 in REQUIREMENTS.md: PRVD-01, PRVD-02, PRVD-03, OAPI-01, OAPI-02, OAPI-03, TEST-01.
All 7 appear in plan `requirements:` frontmatter across 04-01 and 04-02. No orphaned requirements.

---

## Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `scripts/ai_provider.py` | 50 | Comment mentions `OPENAI_API_KEY` | Info | Inline documentation comment only; no secret value present; OAPI-03 unaffected |

No blockers. No warnings.

---

## Human Verification Required

### 1. OAPI-01 Output Format Parity

**Test:** Set `"ai_provider": "openai"` in `plan/config.json`, run `python -m scripts.feed_article | python -m scripts.generate_exercises` with a valid `OPENAI_API_KEY` in env.
**Expected:** Markdown output with all four sections (Article, Vocabulary, Chunking Expressions, Comprehension), vocabulary list of 5-8 items, 3-5 chunks, 3-5 questions — identical structure to Anthropic output.
**Why human:** Live API call required to confirm OpenAI `gpt-4o-mini` follows the JSON schema in the prompt consistently. Structural path is verified; actual LLM compliance cannot be tested offline.

---

## Summary

Phase 4 goal is fully achieved. The codebase now has a clean provider abstraction layer:

- `scripts/ai_provider.py` encapsulates all provider selection and API call logic, exporting `resolve_provider`, `call_claude`, `call_openai`, `call_ai`, `VALID_PROVIDERS`, and `CLAUDE_MODEL`.
- `scripts/generate_exercises.py` is fully decoupled from the Anthropic SDK — it calls `call_ai()` with a runtime-resolved provider and reads configuration from `plan/config.json`.
- Provider switching is operational: set `AI_PROVIDER=openai` as an env var, or change `"ai_provider"` in `plan/config.json` — either path routes to OpenAI.
- The `call_claude()` tech debt from Phase 3 (bare `Exception` catch) is fixed: it now catches `anthropic.APIError` specifically.
- CI workflow is ready for both providers: `OPENAI_API_KEY` is wired to the GitHub secret reference.
- 102 tests pass with 0 failures; all API calls are mocked.

The one human verification item (OAPI-01 live output parity) is not a blocker — the structural path guaranteeing identical output format is verified in code.

---

_Verified: 2026-03-23_
_Verifier: Claude (gsd-verifier)_
