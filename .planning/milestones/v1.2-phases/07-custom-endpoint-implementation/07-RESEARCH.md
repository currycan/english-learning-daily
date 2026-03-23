# Phase 7: Custom Endpoint Implementation - Research

**Researched:** 2026-03-23
**Domain:** Python SDK configuration, env var priority, pytest monkeypatching
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**call_claude() interface**
- Add `base_url=None` and `auth_token=None` optional params to `call_claude(prompt, max_tokens, base_url=None, auth_token=None)`
- Env vars (`ANTHROPIC_BASE_URL`, `ANTHROPIC_AUTH_TOKEN`) are read **inside `call_claude()`** at call time — highest priority, override any params passed in
- Config.json values flow via `model_config` dict: `generate_exercises.py` adds `anthropic_base_url` and `anthropic_auth_token` keys; `_dispatch()` passes them as kwargs to `call_claude()`
- `model_config` in `generate_exercises.py` extended with:
  ```python
  "anthropic_base_url": config.get("anthropic_base_url"),
  "anthropic_auth_token": config.get("anthropic_auth_token"),
  ```

**Anthropic client construction**
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

**CI workflow**
- Add `ANTHROPIC_BASE_URL` and `ANTHROPIC_AUTH_TOKEN` to the `env:` block of `daily-content.yml` unconditionally, same pattern as `ANTHROPIC_API_KEY`:
  ```yaml
  env:
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
    ANTHROPIC_BASE_URL: ${{ secrets.ANTHROPIC_BASE_URL }}
    ANTHROPIC_AUTH_TOKEN: ${{ secrets.ANTHROPIC_AUTH_TOKEN }}
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  ```
- GitHub returns empty string when secret doesn't exist — `call_claude()` treats empty as absent (no conditional YAML needed)

**Test assertions**
- **TEST-01** (custom params path): Assert `anthropic.Anthropic()` constructor was called with `base_url=X, api_key=Y` when env vars are set
- **TEST-02** (backward compat): Assert `anthropic.Anthropic()` is called with **no keyword arguments** when `ANTHROPIC_BASE_URL` and `ANTHROPIC_AUTH_TOKEN` are absent and no config params passed
- Both tests use `monkeypatch` for env vars and `patch("scripts.ai_provider.anthropic.Anthropic")` — consistent with existing test patterns

### Claude's Discretion
- Priority resolution helper naming (e.g., inline vs extracted helper)
- Whether to add a separate test for config.json path (env var absent, config param present)

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| TPROV-01 | call_claude() uses custom base_url when configured (env var or config.json) | Conditional kwargs pattern in `anthropic.Anthropic(base_url=..., api_key=...)` confirmed by existing SDK usage |
| TPROV-02 | call_claude() uses custom auth_token when configured, independent of ANTHROPIC_API_KEY | `api_key` constructor param on `anthropic.Anthropic()` confirmed; env var read order: ANTHROPIC_AUTH_TOKEN > SDK default |
| TPROV-03 | When no custom base_url/auth_token configured, behavior is identical to v1.1 | Conditional kwargs — no args passed when both empty; existing `test_call_claude_raises_provider_error_on_api_error` confirms baseline |
| TPROV-04 | Fallback chain works correctly when primary is a third-party Claude endpoint that raises ProviderError | `call_claude()` already raises `ProviderError`; `_dispatch()` + `call_ai()` fallback logic unchanged |
| CONF-01 | ANTHROPIC_BASE_URL env var is read and applied at highest priority | `os.environ.get("ANTHROPIC_BASE_URL")` inside `call_claude()`, overrides any passed param |
| CONF-02 | ANTHROPIC_AUTH_TOKEN env var is read and applied at highest priority | `os.environ.get("ANTHROPIC_AUTH_TOKEN")` inside `call_claude()`, overrides any passed param |
| CONF-03 | plan/config.json supports anthropic_base_url and anthropic_auth_token fields (lower priority than env vars) | `config.get("anthropic_base_url")` added to `model_config` in `generate_exercises.py`; `_dispatch()` passes to `call_claude()` |
| CONF-04 | GitHub Actions workflow injects ANTHROPIC_BASE_URL and ANTHROPIC_AUTH_TOKEN from repository secrets | Two new lines in `env:` block of `daily-content.yml` "Generate and commit daily content" step |
| TEST-01 | Unit tests verify custom base_url and auth_token are passed to anthropic.Anthropic() client | `patch("scripts.ai_provider.anthropic.Anthropic")` + `assert_called_with(base_url=X, api_key=Y)` |
| TEST-02 | Unit test confirms backward compatibility — missing config falls back to standard Anthropic behavior | `assert_called_with()` (no args) or inspect `call_args` for empty kwargs |
</phase_requirements>

---

## Summary

Phase 7 is a narrow, well-scoped extension to `scripts/ai_provider.py` and `scripts/generate_exercises.py`. The entire change is: (1) teach `call_claude()` to accept and apply `base_url` and `auth_token` parameters that are resolved from env vars at highest priority, (2) wire config.json fallback values through the existing `model_config` dict and `_dispatch()`, and (3) update the CI workflow to pass two new optional secrets.

All three integration points are already fully identified from reading the source: `call_claude()` at line 42 of `ai_provider.py`, `_dispatch()` at line 80, and `model_config` construction at line 134 of `generate_exercises.py`. No new files need to be created — every change lands in an already-existing file.

The decisions are fully prescriptive and leave no ambiguity about implementation shape. The only discretion items are naming and whether to add a third test for the config-path-only scenario (env var absent, config.json value present).

**Primary recommendation:** Implement exactly as specified in CONTEXT.md decisions. The conditional kwargs pattern is idiomatic Python and avoids passing `None` to the SDK. All changes are additive and backward-compatible.

---

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| anthropic | Already in requirements.txt | Claude API client; `anthropic.Anthropic(base_url=..., api_key=...)` constructor accepts custom endpoint | Official Anthropic Python SDK |
| pytest + monkeypatch | Already in requirements.txt | Env var control in tests | Established pattern throughout this codebase |

No new libraries required for this phase.

**Installation:** None — all dependencies already present.

---

## Architecture Patterns

### Existing Project Structure (relevant files)

```
scripts/
├── ai_provider.py          # call_claude(), _dispatch(), call_ai() — PRIMARY CHANGE TARGET
├── generate_exercises.py   # _load_config(), model_config construction — SECONDARY CHANGE TARGET
.github/workflows/
└── daily-content.yml       # env: block — CI CHANGE TARGET
tests/
└── test_ai_provider.py     # New TEST-01, TEST-02 tests go here
plan/
└── config.json             # anthropic_base_url and anthropic_auth_token fields (optional, user-added)
```

### Pattern 1: Conditional kwargs for SDK constructor

**What:** Build kwargs dict only with non-empty values before passing to `anthropic.Anthropic()`.
**When to use:** Any time optional constructor params should only be set when actually configured; avoids `None` overriding SDK defaults.

```python
# Source: CONTEXT.md locked decision + idiomatic Python
def call_claude(prompt: str, max_tokens: int = 2048,
                base_url: str | None = None,
                auth_token: str | None = None) -> str:
    effective_url = os.environ.get("ANTHROPIC_BASE_URL") or base_url or ""
    effective_key = os.environ.get("ANTHROPIC_AUTH_TOKEN") or auth_token or ""
    kwargs: dict = {}
    if effective_url:
        kwargs["base_url"] = effective_url
    if effective_key:
        kwargs["api_key"] = effective_key
    client = anthropic.Anthropic(**kwargs)
    try:
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text
    except anthropic.APIError as e:
        raise ProviderError(f"Claude API call failed: {e}") from e
```

### Pattern 2: Env var priority resolution (existing codebase style)

**What:** Read env var first; fall back to passed param; fall back to empty string. Treat empty string as absent.
**When to use:** Whenever an env var should be the highest-priority override for a value that can also come from config.

```python
# Pattern mirrors existing resolve_provider() which uses:
#   os.environ.get("AI_PROVIDER") or config.get("ai_provider", "anthropic")
effective_url = os.environ.get("ANTHROPIC_BASE_URL") or base_url or ""
```

### Pattern 3: Extending model_config dict (existing pattern)

**What:** Add new keys to the `model_config` dict built in `generate_exercises.py:main()` and passed through `_dispatch()` to `call_claude()`.
**When to use:** Any provider-specific config that must flow from config.json to the provider call function.

```python
# generate_exercises.py — extend existing model_config construction
model_config = {
    "openai_model": config.get("openai_model", "gpt-4o-mini"),
    "anthropic_base_url": config.get("anthropic_base_url"),
    "anthropic_auth_token": config.get("anthropic_auth_token"),
}
```

```python
# ai_provider.py — _dispatch() passes new keys to call_claude()
def _dispatch(prompt: str, provider: str, model_config: dict, max_tokens: int) -> str:
    if provider == "openai":
        return call_openai(prompt, model=model_config["openai_model"], max_tokens=max_tokens)
    return call_claude(
        prompt,
        max_tokens=max_tokens,
        base_url=model_config.get("anthropic_base_url"),
        auth_token=model_config.get("anthropic_auth_token"),
    )
```

### Anti-Patterns to Avoid

- **Passing None to SDK constructor:** `anthropic.Anthropic(base_url=None)` may behave unexpectedly; always use conditional kwargs pattern.
- **Reading env vars at module import time:** Env vars must be read inside `call_claude()` at call time so `monkeypatch.setenv` works in tests (established pattern — `anthropic.Anthropic()` is already instantiated inside the function, not at module level).
- **Storing computed values in plan/state.json:** Not relevant here, but general project constraint — no derived state stored.
- **Mutating model_config dict in place:** Use `model_config.get()` to read values; do not modify the dict.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Custom base URL for Anthropic API | Custom HTTP client or proxy layer | `anthropic.Anthropic(base_url=...)` constructor param | The official SDK already supports this; no custom HTTP needed |
| Secret injection in CI | Custom env-var script in workflow | Standard GitHub Actions `${{ secrets.NAME }}` pattern | Already used for ANTHROPIC_API_KEY and OPENAI_API_KEY in this project |

**Key insight:** The entire feature is a configuration pass-through. The SDK handles all the endpoint routing — the code just needs to pass the right values at construction time.

---

## Common Pitfalls

### Pitfall 1: Empty string treated as truthy in Python
**What goes wrong:** `if base_url:` returns False for empty string, but `or` chaining `os.environ.get("X") or base_url or ""` correctly handles both `None` and `""` as absent.
**Why it happens:** GitHub Actions secrets that don't exist return empty string `""`, not `None`. If the check uses `is not None`, an empty string would be passed to the SDK.
**How to avoid:** Use `or ""` normalization; check with `if effective_url:` (falsy check covers both `None` and `""`).
**Warning signs:** Test passes with `None` but breaks with `""`.

### Pitfall 2: Test-02 assertion shape
**What goes wrong:** `mock.assert_called_with()` (no args) asserts the mock was called with ZERO positional and keyword arguments, which is exactly correct for the backward-compat case.
**Why it happens:** If the kwargs dict is empty (`{}`), `anthropic.Anthropic(**{})` equals `anthropic.Anthropic()`, so `assert_called_with()` is the right assertion.
**How to avoid:** Confirm with `mock.call_args` inspection: `assert mock.call_args == call()` or `assert mock.call_args.kwargs == {}`.

### Pitfall 3: _dispatch() must use .get() not [] for new model_config keys
**What goes wrong:** `model_config["anthropic_base_url"]` raises `KeyError` if existing callers don't pass the new keys (e.g., tests that call `_dispatch()` or `call_ai()` directly with `{"openai_model": "gpt-4o-mini"}`).
**Why it happens:** The existing test suite calls `call_ai()` with `model_config={"openai_model": "gpt-4o-mini"}` (no anthropic keys).
**How to avoid:** Use `model_config.get("anthropic_base_url")` in `_dispatch()` — returns `None` when absent, which `call_claude()` then treats as absent via the `or` chain.

### Pitfall 4: CI env: block placement
**What goes wrong:** Adding new env vars to the top-level `env:` block (lines 8-10) instead of the step-level `env:` block (lines 33-36).
**Why it happens:** The workflow has both a top-level `env:` and a step-level `env:`. Secrets must go in the step-level block where they're used.
**How to avoid:** Add the two new lines directly under the step `env:` block in the "Generate and commit daily content" step, alongside `ANTHROPIC_API_KEY` and `OPENAI_API_KEY`.

---

## Code Examples

Verified patterns from existing source:

### Existing mock pattern for Anthropic constructor (test_ai_provider.py line 90)
```python
# Source: tests/test_ai_provider.py
with patch("scripts.ai_provider.anthropic.Anthropic") as MockAnthropic:
    mock_client = MagicMock()
    MockAnthropic.return_value = mock_client
    mock_client.messages.create.return_value = MagicMock(
        content=[MagicMock(text="response")]
    )
    result = ap.call_claude("prompt")
```

### TEST-01: Assert constructor called with custom params
```python
# Pattern for TEST-01 (custom path)
def test_call_claude_uses_custom_base_url_and_auth_token(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_BASE_URL", "https://custom.example.com")
    monkeypatch.setenv("ANTHROPIC_AUTH_TOKEN", "custom-token-123")
    with patch("scripts.ai_provider.anthropic.Anthropic") as MockAnthropic:
        mock_client = MagicMock()
        MockAnthropic.return_value = mock_client
        mock_client.messages.create.return_value = MagicMock(
            content=[MagicMock(text="response")]
        )
        ap.call_claude("prompt")
    MockAnthropic.assert_called_once_with(
        base_url="https://custom.example.com",
        api_key="custom-token-123",
    )
```

### TEST-02: Assert constructor called with no kwargs (backward compat)
```python
# Pattern for TEST-02 (backward compat)
def test_call_claude_backward_compat_no_custom_config(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_BASE_URL", raising=False)
    monkeypatch.delenv("ANTHROPIC_AUTH_TOKEN", raising=False)
    with patch("scripts.ai_provider.anthropic.Anthropic") as MockAnthropic:
        mock_client = MagicMock()
        MockAnthropic.return_value = mock_client
        mock_client.messages.create.return_value = MagicMock(
            content=[MagicMock(text="response")]
        )
        ap.call_claude("prompt")
    MockAnthropic.assert_called_once_with()  # no args, no kwargs
```

### CI workflow env: block (daily-content.yml)
```yaml
# Source: .github/workflows/daily-content.yml lines 33-36 (existing)
# Add two new lines:
      - name: Generate and commit daily content
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          ANTHROPIC_BASE_URL: ${{ secrets.ANTHROPIC_BASE_URL }}
          ANTHROPIC_AUTH_TOKEN: ${{ secrets.ANTHROPIC_AUTH_TOKEN }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Hardcoded `anthropic.Anthropic()` with no params | `anthropic.Anthropic(**kwargs)` with conditional custom params | Phase 7 | Enables any Claude-compatible third-party endpoint without SDK changes |

**Deprecated/outdated:**
- None — this is a new capability addition, not a replacement.

---

## Open Questions

1. **Optional third test for config-only path**
   - What we know: CONTEXT.md marks this as Claude's discretion
   - What's unclear: Whether to add `test_call_claude_uses_config_base_url_when_no_env_var` that passes `base_url` directly to `call_claude()` without env var set
   - Recommendation: Add it — it's a third distinct code path (env var absent, kwarg present) and costs one extra test function. Documents the priority chain clearly.

2. **Priority helper naming**
   - What we know: Env var resolution logic can be inline (3 lines) or extracted to a small helper
   - What's unclear: User marked this as Claude's discretion
   - Recommendation: Keep inline inside `call_claude()` — the logic is only used once, extracting it adds indirection without benefit. Document with a comment.

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (existing — pytest.ini or setup.cfg not detected, runs via `pytest`) |
| Config file | None detected — uses defaults |
| Quick run command | `pytest tests/test_ai_provider.py -x` |
| Full suite command | `pytest` |

### Phase Requirements to Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| TPROV-01 | call_claude passes base_url to Anthropic() | unit | `pytest tests/test_ai_provider.py::test_call_claude_uses_custom_base_url_and_auth_token -x` | Wave 0 |
| TPROV-02 | call_claude passes api_key to Anthropic() (independent of ANTHROPIC_API_KEY) | unit | `pytest tests/test_ai_provider.py::test_call_claude_uses_custom_base_url_and_auth_token -x` | Wave 0 |
| TPROV-03 | No custom config = identical to v1.1 behavior | unit | `pytest tests/test_ai_provider.py::test_call_claude_backward_compat_no_custom_config -x` | Wave 0 |
| TPROV-04 | Fallback chain works when primary uses third-party endpoint | unit | `pytest tests/test_ai_provider.py -k fallback -x` | Exists (existing fallback tests cover this) |
| CONF-01 | ANTHROPIC_BASE_URL env var applied at highest priority | unit | `pytest tests/test_ai_provider.py::test_call_claude_uses_custom_base_url_and_auth_token -x` | Wave 0 |
| CONF-02 | ANTHROPIC_AUTH_TOKEN env var applied at highest priority | unit | `pytest tests/test_ai_provider.py::test_call_claude_uses_custom_base_url_and_auth_token -x` | Wave 0 |
| CONF-03 | config.json fields flow to call_claude() | unit | `pytest tests/test_ai_provider.py::test_call_claude_uses_config_base_url_when_no_env_var -x` | Wave 0 |
| CONF-04 | CI workflow injects secrets | manual | Inspect daily-content.yml diff | N/A — YAML change, not testable via pytest |
| TEST-01 | Assertions for custom params path | unit | `pytest tests/test_ai_provider.py::test_call_claude_uses_custom_base_url_and_auth_token -x` | Wave 0 |
| TEST-02 | Assertion for backward compat path | unit | `pytest tests/test_ai_provider.py::test_call_claude_backward_compat_no_custom_config -x` | Wave 0 |

### Sampling Rate

- **Per task commit:** `pytest tests/test_ai_provider.py -x`
- **Per wave merge:** `pytest`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps

- [ ] `tests/test_ai_provider.py` — add `test_call_claude_uses_custom_base_url_and_auth_token` (TEST-01, TPROV-01, TPROV-02, CONF-01, CONF-02)
- [ ] `tests/test_ai_provider.py` — add `test_call_claude_backward_compat_no_custom_config` (TEST-02, TPROV-03)
- [ ] `tests/test_ai_provider.py` — add `test_call_claude_uses_config_base_url_when_no_env_var` (CONF-03, Claude's discretion)

No new test files needed — all new tests go into the existing `tests/test_ai_provider.py`.

---

## Sources

### Primary (HIGH confidence)

- `scripts/ai_provider.py` — Current `call_claude()`, `_dispatch()`, `call_ai()` — read directly
- `scripts/generate_exercises.py` lines 113-134 — `_load_config()` and `model_config` — read directly
- `tests/test_ai_provider.py` — Existing mock/monkeypatch patterns — read directly
- `.github/workflows/daily-content.yml` — Current env: block structure — read directly
- `plan/config.json` — Current schema (no anthropic_base_url / anthropic_auth_token fields yet) — read directly
- `.planning/phases/07-custom-endpoint-implementation/07-CONTEXT.md` — Locked decisions — read directly

### Secondary (MEDIUM confidence)

- None required — all decisions are fully specified in CONTEXT.md and all source files were directly inspected.

### Tertiary (LOW confidence)

- None.

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — no new libraries; all changes are in existing files using established patterns
- Architecture: HIGH — all integration points identified by direct source reading; no ambiguity
- Pitfalls: HIGH — derived from direct inspection of existing test patterns and Python truthiness behavior
- Test patterns: HIGH — existing `patch("scripts.ai_provider.anthropic.Anthropic")` pattern confirmed in test_ai_provider.py line 90

**Research date:** 2026-03-23
**Valid until:** 2026-06-23 (stable — no fast-moving dependencies)
