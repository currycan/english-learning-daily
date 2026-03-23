# Phase 7: Custom Endpoint Implementation - Context

**Gathered:** 2026-03-23
**Status:** Ready for planning

<domain>
## Phase Boundary

Extend `call_claude()` in `scripts/ai_provider.py` to pass `base_url` and `api_key` to `anthropic.Anthropic()` when configured via env vars or `config.json` fields. Full backward compatibility required — when no custom values are configured, behavior is identical to v1.1. Tests embedded per TDD practice. CI workflow updated to inject the two new optional secrets.

</domain>

<decisions>
## Implementation Decisions

### call_claude() interface
- Add `base_url=None` and `auth_token=None` optional params to `call_claude(prompt, max_tokens, base_url=None, auth_token=None)`
- Env vars (`ANTHROPIC_BASE_URL`, `ANTHROPIC_AUTH_TOKEN`) are read **inside `call_claude()`** at call time — highest priority, override any params passed in
- Config.json values flow via `model_config` dict: `generate_exercises.py` adds `anthropic_base_url` and `anthropic_auth_token` keys; `_dispatch()` passes them as kwargs to `call_claude()`
- `model_config` in `generate_exercises.py` extended with:
  ```python
  "anthropic_base_url": config.get("anthropic_base_url"),
  "anthropic_auth_token": config.get("anthropic_auth_token"),
  ```

### Anthropic client construction
- Use **conditional kwargs** — only pass `base_url`/`api_key` to `anthropic.Anthropic()` when non-empty:
  ```python
  kwargs = {}
  if effective_url:
      kwargs["base_url"] = effective_url
  if effective_key:
      kwargs["api_key"] = effective_key
  client = anthropic.Anthropic(**kwargs)
  ```
- This avoids passing `None` which could override SDK defaults unexpectedly

### CI workflow
- Add `ANTHROPIC_BASE_URL` and `ANTHROPIC_AUTH_TOKEN` to the `env:` block of `daily-content.yml` **unconditionally**, same pattern as `ANTHROPIC_API_KEY`:
  ```yaml
  env:
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
    ANTHROPIC_BASE_URL: ${{ secrets.ANTHROPIC_BASE_URL }}
    ANTHROPIC_AUTH_TOKEN: ${{ secrets.ANTHROPIC_AUTH_TOKEN }}
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  ```
- GitHub returns empty string when secret doesn't exist — `call_claude()` treats empty as absent (no conditional YAML needed)

### Test assertions (TEST-01 and TEST-02)
- **TEST-01** (custom params path): Assert `anthropic.Anthropic()` constructor was called with `base_url=X, api_key=Y` when env vars are set
- **TEST-02** (backward compat): Assert `anthropic.Anthropic()` is called with **no keyword arguments** when `ANTHROPIC_BASE_URL` and `ANTHROPIC_AUTH_TOKEN` are absent and no config params passed
- Both tests use `monkeypatch` for env vars and `patch("scripts.ai_provider.anthropic.Anthropic")` — consistent with existing test patterns

### Claude's Discretion
- Priority resolution helper naming (e.g., inline vs extracted helper)
- Whether to add a separate test for config.json path (env var absent, config param present)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements
- `.planning/REQUIREMENTS.md` — TPROV-01 through TPROV-04, CONF-01 through CONF-04, TEST-01, TEST-02

### Existing implementation
- `scripts/ai_provider.py` — Current `call_claude()`, `_dispatch()`, `call_ai()` implementation to extend
- `scripts/generate_exercises.py` lines 113–137 — `_load_config()` and `model_config` construction to update
- `tests/test_ai_provider.py` — Existing test patterns (`patch("scripts.ai_provider.anthropic.Anthropic")`, `monkeypatch`, `MagicMock`)

### CI
- `.github/workflows/daily-content.yml` — Workflow file to update with new env var injections

No external specs — requirements are fully captured in decisions above.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `call_claude(prompt, max_tokens)` in `ai_provider.py` — the function being extended; currently calls `anthropic.Anthropic()` with no args
- `_dispatch(prompt, provider, model_config, max_tokens)` — already receives `model_config`; passes `model_config["openai_model"]` to `call_openai` — same pattern for new Anthropic keys
- `model_config` dict in `generate_exercises.py` — already aggregates provider-specific config; extend with two new keys

### Established Patterns
- `anthropic.Anthropic()` instantiated inside `call_claude()` — testability pattern; DO NOT move to module level
- `patch("scripts.ai_provider.anthropic.Anthropic")` — mock pattern in tests; TEST-01/02 must use this
- `monkeypatch.setenv` / `monkeypatch.delenv` — used throughout test suite for env var control
- Conditional kwargs (`**kwargs`) — idiomatic Python; avoids passing None to SDK

### Integration Points
- `generate_exercises.py:main()` — only place where `model_config` is built from config; add two keys here
- `_dispatch()` in `ai_provider.py` — routes to `call_claude()`; add `base_url` and `auth_token` kwargs here
- `daily-content.yml` `env:` block in "Generate and commit daily content" step — add two new secrets here

</code_context>

<specifics>
## Specific Ideas

No specific requirements — open to standard approaches.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 07-custom-endpoint-implementation*
*Context gathered: 2026-03-23*
