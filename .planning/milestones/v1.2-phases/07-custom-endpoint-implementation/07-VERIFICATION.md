---
phase: 07-custom-endpoint-implementation
verified: 2026-03-23T00:00:00Z
status: passed
score: 12/12 must-haves verified
re_verification: false
---

# Phase 7: Custom Endpoint Implementation — Verification Report

**Phase Goal:** Users can point call_claude() at any Claude-compatible third-party API endpoint by setting two env vars or config.json fields, with full backward compatibility preserved
**Verified:** 2026-03-23
**Status:** passed
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | call_claude() accepts base_url=None and auth_token=None optional parameters | VERIFIED | `scripts/ai_provider.py` lines 44-46: `base_url: str \| None = None, auth_token: str \| None = None` |
| 2 | ANTHROPIC_BASE_URL env var is read and applied at highest priority | VERIFIED | `ai_provider.py` line 55: `effective_url = os.environ.get("ANTHROPIC_BASE_URL") or base_url or ""` |
| 3 | ANTHROPIC_AUTH_TOKEN env var is read and applied at highest priority | VERIFIED | `ai_provider.py` line 56: `effective_key = os.environ.get("ANTHROPIC_AUTH_TOKEN") or auth_token or ""` |
| 4 | anthropic.Anthropic() is constructed with conditional kwargs — base_url and api_key only when non-empty | VERIFIED | `ai_provider.py` lines 58-63: conditional kwargs dict pattern, `client = anthropic.Anthropic(**kwargs)` |
| 5 | When no env vars and no kwargs, anthropic.Anthropic() is called with zero arguments | VERIFIED | test_call_claude_backward_compat_no_custom_config passes: MockAnthropic.assert_called_once_with() |
| 6 | _dispatch() passes anthropic_base_url and anthropic_auth_token from model_config to call_claude() | VERIFIED | `ai_provider.py` lines 103-108: `base_url=model_config.get("anthropic_base_url"), auth_token=model_config.get("anthropic_auth_token")` |
| 7 | generate_exercises.py model_config dict includes anthropic_base_url and anthropic_auth_token from config.get() | VERIFIED | `generate_exercises.py` lines 136-137: both keys present with config.get() |
| 8 | All three new tests from Plan 01 are GREEN | VERIFIED | pytest 20/20 passed in test_ai_provider.py |
| 9 | ANTHROPIC_BASE_URL env var injected into CI step from secrets.ANTHROPIC_BASE_URL | VERIFIED | `.github/workflows/daily-content.yml` line 35: `ANTHROPIC_BASE_URL: ${{ secrets.ANTHROPIC_BASE_URL }}` |
| 10 | ANTHROPIC_AUTH_TOKEN env var injected into CI step from secrets.ANTHROPIC_AUTH_TOKEN | VERIFIED | `.github/workflows/daily-content.yml` line 36: `ANTHROPIC_AUTH_TOKEN: ${{ secrets.ANTHROPIC_AUTH_TOKEN }}` |
| 11 | Both new lines are in the step-level env block, NOT the top-level env block | VERIFIED | Top-level env block (line 8-9) contains only FORCE_JAVASCRIPT_ACTIONS_TO_NODE24; new vars are under the "Generate and commit daily content" step |
| 12 | Existing ANTHROPIC_API_KEY and OPENAI_API_KEY lines are unchanged | VERIFIED | Both present at lines 34 and 37 |

**Score:** 12/12 truths verified

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `tests/test_ai_provider.py` | Three new test functions covering TEST-01, TEST-02, CONF-03 | VERIFIED | All three functions exist at lines 180-228; substantive assertions using MockAnthropic.assert_called_once_with(); wired via patch("scripts.ai_provider.anthropic.Anthropic") + monkeypatch |
| `scripts/ai_provider.py` | Extended call_claude() and updated _dispatch() | VERIFIED | Signature at lines 42-47 includes base_url and auth_token; _dispatch() at lines 103-108 uses model_config.get() for both keys; full implementation — not a stub |
| `scripts/generate_exercises.py` | model_config extended with anthropic fields | VERIFIED | Lines 134-138 include both anthropic_base_url and anthropic_auth_token from config.get(); wired to call_ai() at line 141 |
| `.github/workflows/daily-content.yml` | CI injects two new optional secrets as env vars | VERIFIED | Lines 35-36 present in step-level env block; YAML is structurally valid |

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `tests/test_ai_provider.py` | `scripts/ai_provider.call_claude` | `patch('scripts.ai_provider.anthropic.Anthropic') + monkeypatch.setenv` | WIRED | MockAnthropic.assert_called_once_with() present 3 times at lines 193, 212, 228 |
| `scripts/generate_exercises.py` | `scripts/ai_provider._dispatch` | `model_config dict with anthropic_base_url and anthropic_auth_token keys` | WIRED | model_config passed at line 141 via call_ai(); _dispatch() consumes via model_config.get() |
| `scripts/ai_provider._dispatch` | `scripts/ai_provider.call_claude` | `base_url and auth_token kwargs` | WIRED | Lines 103-108: both kwargs explicitly passed using .get() |
| `scripts/ai_provider.call_claude` | `anthropic.Anthropic` | `conditional kwargs dict` | WIRED | Lines 58-63: kwargs["base_url"] and kwargs["api_key"] set conditionally, then `anthropic.Anthropic(**kwargs)` |
| `.github/workflows/daily-content.yml step env` | `scripts/ai_provider.call_claude` | `os.environ.get('ANTHROPIC_BASE_URL') inside call_claude()` | WIRED | Secret injected at CI level (line 35-36); consumed at ai_provider.py line 55-56 via os.environ.get |

---

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| TPROV-01 | 07-01, 07-02 | call_claude() uses custom base_url when configured (env var or config.json) | SATISFIED | ai_provider.py lines 55, 59-60: env var read, conditionally passed to Anthropic() |
| TPROV-02 | 07-01, 07-02 | call_claude() uses custom auth_token when configured, independent of ANTHROPIC_API_KEY | SATISFIED | ai_provider.py lines 56, 61-62: ANTHROPIC_AUTH_TOKEN mapped to api_key, independent of ANTHROPIC_API_KEY |
| TPROV-03 | 07-01, 07-02 | When no custom base_url/auth_token configured, behavior identical to v1.1 | SATISFIED | test_call_claude_backward_compat_no_custom_config passes: Anthropic() called with zero args |
| TPROV-04 | 07-02, 07-03 | Fallback chain works correctly when primary provider uses a third-party Claude endpoint | SATISFIED | _dispatch() passes anthropic_base_url/auth_token from model_config to call_claude(); fallback to OpenAI via _backup_provider() unaffected; 4 fallback tests pass |
| CONF-01 | 07-01, 07-02 | ANTHROPIC_BASE_URL env var is read and applied at highest priority | SATISFIED | ai_provider.py line 55: `os.environ.get("ANTHROPIC_BASE_URL") or base_url or ""` — env var wins |
| CONF-02 | 07-01, 07-02 | ANTHROPIC_AUTH_TOKEN env var is read and applied at highest priority | SATISFIED | ai_provider.py line 56: `os.environ.get("ANTHROPIC_AUTH_TOKEN") or auth_token or ""` — env var wins |
| CONF-03 | 07-01, 07-02 | plan/config.json supports anthropic_base_url and anthropic_auth_token fields (lower priority than env vars) | SATISFIED | generate_exercises.py lines 136-137: config.get("anthropic_base_url") and config.get("anthropic_auth_token") passed through model_config; env var priority enforced in call_claude() |
| CONF-04 | 07-03 | GitHub Actions workflow injects ANTHROPIC_BASE_URL and ANTHROPIC_AUTH_TOKEN from repository secrets | SATISFIED | daily-content.yml lines 35-36 in step-level env block |
| TEST-01 | 07-01 | Unit tests verify custom base_url and auth_token are passed to anthropic.Anthropic() client | SATISFIED | test_call_claude_uses_custom_base_url_and_auth_token exists and passes |
| TEST-02 | 07-01 | Unit test confirms backward compatibility — missing config falls back to standard Anthropic behavior | SATISFIED | test_call_claude_backward_compat_no_custom_config exists and passes |

**Orphaned requirements check:** REQUIREMENTS.md maps all 10 IDs to Phase 7 (TPROV-01 through CONF-04 plus TEST-01, TEST-02). All 10 are claimed across the three plans and verified above. No orphans.

Note: TPROV-05 (multiple named third-party profiles) appears in REQUIREMENTS.md but is explicitly scoped to a future phase — not assigned to Phase 7.

---

### Anti-Patterns Found

None. No TODO, FIXME, placeholder, empty return, or stub patterns found in any phase-modified file.

---

### Human Verification Required

None required. All behavioral contracts are verified programmatically:
- Unit tests exercise env var priority, backward compat, and kwarg-only path
- Full suite (118 tests) passes with zero failures
- YAML structure verified by inspection
- Key wiring traced end-to-end through the call chain

---

## Gaps Summary

No gaps. All 12 must-haves are verified, all 10 requirement IDs are satisfied, the full test suite (118 tests) passes, and no anti-patterns were found in the modified files.

The phase goal is fully achieved: users can point call_claude() at any Claude-compatible third-party endpoint by setting ANTHROPIC_BASE_URL and ANTHROPIC_AUTH_TOKEN as env vars or as fields in plan/config.json, with existing callers unaffected.

---

_Verified: 2026-03-23_
_Verifier: Claude (gsd-verifier)_
