# Phase 1: Gemini Migration - Research

**Researched:** 2026-03-24
**Domain:** Python AI provider replacement — `google-genai` SDK, test rewriting, CI secret rotation
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** 使用 `google-genai`（新官方 SDK，`pip install google-genai`），不用旧版 `google-generativeai`。
  - Import: `from google import genai`
  - 客户端实例化在函数内部（符合现有模式，便于 mock 测试）：`client = genai.Client(api_key=key)`
  - 调用：`client.models.generate_content(model=..., contents=prompt)`
  - 返回文本：`response.text`
- **D-02:** 默认模型 `gemini-2.0-flash-lite`，成本最低，适合每天一次调用。
  - Config 字段：`gemini_model: "gemini-2.0-flash-lite"`（可覆盖）
  - 代码常量 `GEMINI_MODEL = "gemini-2.0-flash-lite"` 作为 fallback
- **D-03:** 完全删除 fallback 逻辑。移除 `_backup_provider()`、`_dispatch()`、`call_ai()` 的 retry 路径。
  - 替换为单一函数 `call_gemini(prompt, ...)` 返回文本，失败抛 `ProviderError`
  - `generate_exercises.py` 直接调用 `call_gemini()`，失败时 `sys.exit(1)`
  - 保留 `ProviderError` 异常类（语义清晰）
- **D-04:** 环境变量 `GEMINI_API_KEY`（不用 `GOOGLE_API_KEY`）
  - Priority: `os.environ.get("GEMINI_API_KEY") or config.get("gemini_api_key") or ""`
  - Config 字段：`gemini_model`（替换 `claude_model` / `openai_model`）
  - 删除的 config 字段：`ai_provider`, `openai_model`, `claude_model`, `anthropic_base_url`, `anthropic_auth_token`
  - 删除的 env vars：`ANTHROPIC_API_KEY`, `ANTHROPIC_BASE_URL`, `ANTHROPIC_AUTH_TOKEN`, `OPENAI_API_KEY`

### Claude's Discretion

- `google-genai` SDK 的确切 pip 版本号（选最新稳定版）
- docs/ai-providers.md 更新范围（保持双语格式，与现有风格一致）
- 测试 mock 策略（遵循现有 `call_gemini()` 函数内实例化客户端的模式）

### Deferred Ideas (OUT OF SCOPE)

None — discussion stayed within phase scope
</user_constraints>

---

## Summary

This phase replaces the dual-provider (Claude + OpenAI) architecture in `scripts/ai_provider.py` with a single Gemini-only provider using the `google-genai` SDK. All related code, configuration, CI secrets, dependencies, tests, and documentation must be updated in coordination. The scope is well-defined and every file to be changed has been examined.

The existing codebase follows clean patterns: SDK clients are instantiated inside functions for testability, `ProviderError` is raised at the call level and caught at the `main()` level with `sys.exit(1)`, and error output goes to `sys.stderr` with `INFO`/`WARNING`/`ERROR` prefixes. The new `call_gemini()` must preserve all of these conventions.

The test rewrite is the most structurally significant change: `test_ai_provider.py` currently tests `resolve_provider`, `call_claude`, `call_openai`, `call_ai`, fallback logic, and custom endpoint behavior. All of these must be replaced with tests for `call_gemini` and its mock pattern. `test_ai_provider_docs.py` asserts on specific strings in `docs/ai-providers.md` that reference old provider names — those assertions must be replaced wholesale.

**Primary recommendation:** Implement in file order: `requirements.txt` → `scripts/ai_provider.py` → `scripts/generate_exercises.py` → `plan/config.json` → `.github/workflows/daily-content.yml` → `tests/test_ai_provider.py` → `tests/test_ai_provider_docs.py` → `docs/ai-providers.md`. Always write tests RED-first for the new `call_gemini` behavior before implementing.

---

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| google-genai | 1.68.0 | Official Google Gemini Python SDK | Locked decision D-01; replaces anthropic + openai |
| pytest | 8.3.5 (already pinned) | Test framework | Already in requirements.txt |

**Version verification:** `google-genai` 1.68.0 verified against PyPI on 2026-03-24 (released 2026-03-18).

**Packages to REMOVE:**
- `anthropic==0.86.0`
- `openai==2.29.0`

**Package to ADD:**
- `google-genai==1.68.0`

### Installation

```bash
pip install google-genai==1.68.0
```

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| google-genai | google-generativeai | Old SDK, deprecated; D-01 explicitly excludes it |
| GEMINI_API_KEY env var | GOOGLE_API_KEY | D-04 explicitly chose GEMINI_API_KEY for clarity |

---

## Architecture Patterns

### New `scripts/ai_provider.py` Structure

```
scripts/ai_provider.py
  ProviderError           # keep — semantics unchanged
  GEMINI_MODEL            # constant: "gemini-2.0-flash-lite"
  call_gemini(prompt, max_tokens, model, api_key) -> str
    # resolves key: os.environ.get("GEMINI_API_KEY") or api_key or ""
    # instantiates client = genai.Client(api_key=key) inside function
    # calls client.models.generate_content(model=..., contents=prompt)
    # returns response.text
    # catches genai errors, raises ProviderError
```

**Removed from `ai_provider.py`:**
- `resolve_provider()`
- `call_claude()`
- `call_openai()`
- `_backup_provider()`
- `_dispatch()`
- `call_ai()`
- `VALID_PROVIDERS`, `CLAUDE_MODEL` constants
- `import anthropic`, `import openai`

### Pattern 1: Gemini Client Instantiation (inside function)

**What:** Client is created fresh inside `call_gemini()` on every call, not at module level.
**When to use:** Always — this is the established project pattern for testability (mocking is simpler when the constructor is called inside the function under test).

```python
# Source: CONTEXT.md D-01, confirmed by google-genai 1.68.0 docs
from google import genai
from scripts.ai_provider import ProviderError

GEMINI_MODEL = "gemini-2.0-flash-lite"


def call_gemini(
    prompt: str,
    max_tokens: int = 2048,
    model: str | None = None,
    api_key: str | None = None,
) -> str:
    key = os.environ.get("GEMINI_API_KEY") or api_key or ""
    effective_model = model or GEMINI_MODEL
    print(f"INFO: Gemini model: {effective_model}", file=sys.stderr)
    client = genai.Client(api_key=key)
    try:
        response = client.models.generate_content(
            model=effective_model,
            contents=prompt,
        )
        return response.text
    except Exception as e:
        raise ProviderError(f"Gemini API call failed: {e}") from e
```

### Pattern 2: `generate_exercises.py` Wiring

**What:** Replace `resolve_provider()` + `call_ai()` with direct `call_gemini()` call.
**When to use:** In `main()`.

```python
# Before:
provider = resolve_provider(config)
model_config = {
    "openai_model": config.get("openai_model", "gpt-4o-mini"),
    "claude_model": config.get("claude_model"),
    "anthropic_base_url": config.get("anthropic_base_url"),
    "anthropic_auth_token": config.get("anthropic_auth_token"),
}
raw_response = call_ai(prompt, provider=provider, model_config=model_config)

# After:
raw_response = call_gemini(prompt, model=config.get("gemini_model"))
```

The import line changes from:
```python
from scripts.ai_provider import call_ai, resolve_provider
```
to:
```python
from scripts.ai_provider import call_gemini, ProviderError
```

And `ProviderError` should be caught in `main()` with `sys.exit(1)`.

### Pattern 3: Mock Strategy for Tests

**What:** Patch `genai.Client` at the module level where it is used.
**When to use:** All `call_gemini` unit tests.

```python
# Source: established project pattern (same as existing call_claude / call_openai mocks)
from unittest.mock import patch, MagicMock
import scripts.ai_provider as ap

def test_call_gemini_returns_text():
    with patch("scripts.ai_provider.genai.Client") as MockClient:
        mock_client = MagicMock()
        MockClient.return_value = mock_client
        mock_client.models.generate_content.return_value = MagicMock(text="response text")
        result = ap.call_gemini("test prompt")
    assert result == "response text"
```

### Anti-Patterns to Avoid

- **Instantiating `genai.Client()` at module level:** Makes unit testing impossible without patching at import time. Always instantiate inside `call_gemini()`.
- **Catching only specific Gemini exception types:** The `google-genai` exception hierarchy differs from `anthropic.APIError`. Catch broad `Exception` and re-raise as `ProviderError` (same pattern as existing `call_openai`).
- **Leaving old import lines:** `import anthropic` and `import openai` at the top of `ai_provider.py` will fail once those packages are removed from `requirements.txt`. Remove both.
- **Leaving old test assertions in `test_ai_provider_docs.py`:** The existing docs test file asserts on strings like `"ANTHROPIC_API_KEY"`, `"console.anthropic.com"`, `"OPENAI_API_KEY"`, `"ai_provider"`, and `"AI_PROVIDER"` — all of which will be absent from the new `docs/ai-providers.md`. Rewrite all assertions.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| API key injection from env | Custom env var parsing | `os.environ.get("GEMINI_API_KEY")` | Already standard; matches D-04 pattern |
| HTTP client for Gemini | Direct requests calls | `genai.Client` | SDK handles auth, retry headers, response parsing |
| Exception wrapping | Custom error types | Re-use `ProviderError` | Already in codebase; semantically correct |

**Key insight:** The `google-genai` SDK wraps all HTTP-level concerns. Do not write raw `requests` calls to the Gemini REST endpoint.

---

## Common Pitfalls

### Pitfall 1: `google-generativeai` vs `google-genai` confusion

**What goes wrong:** Wrong package installed; `from google.generativeai import ...` instead of `from google import genai`.
**Why it happens:** Old SDK (`google-generativeai`) is still on PyPI and has similar name. Many tutorials reference it.
**How to avoid:** D-01 explicitly mandates `google-genai`. Use `pip install google-genai==1.68.0` and verify with `pip show google-genai`.
**Warning signs:** `ImportError: cannot import name 'Client' from 'google.generativeai'` — that's the old SDK.

### Pitfall 2: Stale test assertions in `test_ai_provider_docs.py`

**What goes wrong:** Tests pass with old docs file but fail after docs update, or tests are deleted but coverage drops.
**Why it happens:** The docs test file is tightly coupled to specific strings in `docs/ai-providers.md`. Every assertion in the file references strings that will not exist in the new Gemini-only docs.
**How to avoid:** Rewrite all test cases in `test_ai_provider_docs.py` before updating the docs file. Write RED tests first (they will fail on old content), then update the docs.
**Warning signs:** All doc tests passing while the docs still reference `ANTHROPIC_API_KEY` — that means the test suite was not actually updated.

### Pitfall 3: `generate_exercises.py` error messages still reference "Claude"

**What goes wrong:** Error messages like `"ERROR: Claude returned invalid JSON"` remain in `parse_response()` after the migration.
**Why it happens:** `parse_response()` is not in scope per CONTEXT.md but its error messages contain provider-specific language.
**How to avoid:** Update error message strings in `parse_response()` to be provider-neutral (e.g., `"ERROR: AI returned invalid JSON"`). This is a small change but prevents confusing error logs.
**Warning signs:** `grep -r "Claude" scripts/` returning matches after the migration.

### Pitfall 4: CI workflow still injects deleted secrets

**What goes wrong:** `daily-content.yml` keeps `ANTHROPIC_API_KEY`, `ANTHROPIC_BASE_URL`, `ANTHROPIC_AUTH_TOKEN`, `OPENAI_API_KEY` env injections. These resolve to empty strings in GitHub Actions (secrets are optional), so no error is raised — but the workflow silently passes unused variables.
**Why it happens:** YAML env blocks are additive; extra entries don't fail.
**How to avoid:** Explicitly remove all four old `env:` lines from the generate step and add `GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}`.
**Warning signs:** `grep -n "ANTHROPIC\|OPENAI" .github/workflows/daily-content.yml` returning matches after migration.

### Pitfall 5: `plan/config.json` old fields not cleaned up

**What goes wrong:** `ai_provider`, `openai_model`, `claude_model` fields remain in `config.json`. They are harmless but misleading and may confuse future maintainers.
**Why it happens:** Easy to forget config field cleanup when the code changes work correctly.
**How to avoid:** Per D-04, remove all four old fields and add `gemini_model`.
**Warning signs:** `"ai_provider"` key present in `plan/config.json` after migration.

---

## Code Examples

### Verified: google-genai basic call pattern

```python
# Source: PyPI google-genai 1.68.0 (verified 2026-03-24)
from google import genai

client = genai.Client(api_key="GEMINI_API_KEY")
response = client.models.generate_content(
    model="gemini-2.0-flash-lite",
    contents="your prompt here",
)
text = response.text
```

### Verified: Test mock pattern (matching project conventions)

```python
# Source: Derived from existing test_ai_provider.py mock pattern
from unittest.mock import patch, MagicMock
import scripts.ai_provider as ap

def test_call_gemini_returns_text():
    with patch("scripts.ai_provider.genai.Client") as MockClient:
        mock_client = MagicMock()
        MockClient.return_value = mock_client
        mock_client.models.generate_content.return_value = MagicMock(text="response")
        result = ap.call_gemini("prompt")
    assert result == "response"

def test_call_gemini_raises_provider_error_on_failure():
    with patch("scripts.ai_provider.genai.Client") as MockClient:
        mock_client = MagicMock()
        MockClient.return_value = mock_client
        mock_client.models.generate_content.side_effect = Exception("api down")
        with pytest.raises(ap.ProviderError):
            ap.call_gemini("prompt")

def test_call_gemini_uses_env_api_key(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key-123")
    with patch("scripts.ai_provider.genai.Client") as MockClient:
        mock_client = MagicMock()
        MockClient.return_value = mock_client
        mock_client.models.generate_content.return_value = MagicMock(text="ok")
        ap.call_gemini("prompt")
    MockClient.assert_called_once_with(api_key="test-key-123")

def test_call_gemini_uses_default_model():
    with patch("scripts.ai_provider.genai.Client") as MockClient:
        mock_client = MagicMock()
        MockClient.return_value = mock_client
        mock_client.models.generate_content.return_value = MagicMock(text="ok")
        ap.call_gemini("prompt")
    call_kwargs = mock_client.models.generate_content.call_args
    assert call_kwargs.kwargs.get("model") == "gemini-2.0-flash-lite"
```

### Verified: Config fields before/after

```json
// BEFORE (to be replaced entirely)
{
  "morning_hour": 7,
  "evening_hour": 21,
  "weekly_recording_day": "saturday",
  "timezone": "Asia/Shanghai",
  "ai_provider": "anthropic",
  "openai_model": "gpt-4o-mini",
  "claude_model": "claude-haiku-4-5-20251001",
  "content_feeds": { ... }
}

// AFTER
{
  "morning_hour": 7,
  "evening_hour": 21,
  "weekly_recording_day": "saturday",
  "timezone": "Asia/Shanghai",
  "gemini_model": "gemini-2.0-flash-lite",
  "content_feeds": { ... }
}
```

### Verified: CI env block before/after

```yaml
# BEFORE
- name: Generate and commit daily content
  env:
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
    ANTHROPIC_BASE_URL: ${{ secrets.ANTHROPIC_BASE_URL }}
    ANTHROPIC_AUTH_TOKEN: ${{ secrets.ANTHROPIC_AUTH_TOKEN }}
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}

# AFTER
- name: Generate and commit daily content
  env:
    GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
```

---

## Files to Change — Complete Inventory

| File | Change Type | Summary |
|------|-------------|---------|
| `requirements.txt` | Replace deps | Remove `anthropic`, `openai`; add `google-genai==1.68.0` |
| `scripts/ai_provider.py` | Full rewrite | Single `call_gemini()`, keep `ProviderError`, remove all other code |
| `scripts/generate_exercises.py` | Targeted edits | Update import, remove `model_config` dict, call `call_gemini()` directly |
| `plan/config.json` | Field swap | Remove 4 old fields, add `gemini_model` |
| `.github/workflows/daily-content.yml` | Env block swap | Remove 4 old secrets, add `GEMINI_API_KEY` |
| `tests/test_ai_provider.py` | Full rewrite | Replace all 15+ tests with Gemini-specific tests |
| `tests/test_ai_provider_docs.py` | Full rewrite | Replace all assertions with Gemini doc assertions |
| `docs/ai-providers.md` | Full rewrite | Gemini-only content, bilingual EN+ZH format |

---

## State of the Art

| Old Approach | Current Approach | Impact |
|--------------|------------------|--------|
| `google-generativeai` (genai v1) | `google-genai` (new unified SDK) | New import path: `from google import genai` not `import google.generativeai` |
| Multi-provider fallback | Single-provider, fail-fast | Simpler code, clearer failure modes for CI |

**Deprecated/outdated:**
- `google-generativeai`: Old SDK, superceded by `google-genai`. Do not use.
- `AI_PROVIDER` env var: Removed in this phase — only one provider now.

---

## Open Questions

1. **`parse_response()` error message wording**
   - What we know: Error messages contain "Claude" (e.g., `"ERROR: Claude returned invalid JSON"`).
   - What's unclear: Whether CONTEXT.md scope includes updating these strings (it does not explicitly call them out).
   - Recommendation: Update to provider-neutral wording (`"ERROR: AI returned invalid JSON"`) as part of `generate_exercises.py` edits — minimal effort, avoids misleading error logs.

2. **GitHub Actions secret `GEMINI_API_KEY` must be pre-created**
   - What we know: The workflow will fail if `GEMINI_API_KEY` is not set in GitHub repository secrets.
   - What's unclear: Whether the secret already exists in the repository (cannot verify from code).
   - Recommendation: Add a note in the plan that the human operator must add `GEMINI_API_KEY` secret in GitHub Settings before the workflow runs. This is a manual step not automatable by code changes.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.12 | CI (setup-python@v5) | ✓ (CI pinned) | 3.12 | — |
| Python 3.10+ | google-genai SDK minimum | ✓ | macOS has 3.14 locally | — |
| pytest | test suite | pinned in requirements.txt | 8.3.5 | — |
| google-genai | Gemini calls | Not yet installed (to be added) | 1.68.0 target | — |
| GEMINI_API_KEY secret | GitHub Actions workflow | Unknown — requires human to add | — | Workflow fails without it |

**Missing dependencies with no fallback:**
- `GEMINI_API_KEY` GitHub Actions secret — must be manually created by repository owner before CI can run. This is outside code changes.

**Missing dependencies with fallback:**
- None.

---

## Project Constraints (from CLAUDE.md)

Directives from `CLAUDE.md` that the planner must verify compliance with:

- **Immutability:** `state.json` mutations use `copy.deepcopy`. `apply_command()` must not modify its input. (Not directly relevant to this phase — no state.json changes.)
- **No secrets in code:** `GEMINI_API_KEY` comes from environment only. Must not appear in `plan/config.json`, `requirements.txt`, or any committed file.
- **Derived state:** Do not add computed fields to `state.json`. (Not applicable here.)
- **Exit non-zero on failure:** `call_gemini()` raises `ProviderError`; `main()` in `generate_exercises.py` must catch and `sys.exit(1)`. Verified as the existing and required pattern.
- **Scripts runnable with `-m`:** `python -m scripts.generate_exercises` must continue to work after refactor.
- **Communication language:** Code comments and docs content follow project conventions (bilingual EN+ZH for docs).

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 8.3.5 |
| Config file | none (pytest.ini not present; uses default discovery) |
| Quick run command | `pytest tests/test_ai_provider.py tests/test_ai_provider_docs.py -x` |
| Full suite command | `pytest` |

### Phase Requirements to Test Map

| Behavior | Test Type | Automated Command | File Exists? |
|----------|-----------|-------------------|--------------|
| `call_gemini()` returns text on success | unit | `pytest tests/test_ai_provider.py -x` | Wave 0 rewrite |
| `call_gemini()` raises `ProviderError` on API failure | unit | `pytest tests/test_ai_provider.py -x` | Wave 0 rewrite |
| `call_gemini()` uses `GEMINI_API_KEY` env var | unit | `pytest tests/test_ai_provider.py -x` | Wave 0 rewrite |
| `call_gemini()` uses `gemini-2.0-flash-lite` default model | unit | `pytest tests/test_ai_provider.py -x` | Wave 0 rewrite |
| `call_gemini()` accepts model override | unit | `pytest tests/test_ai_provider.py -x` | Wave 0 rewrite |
| `generate_exercises.main()` calls `call_gemini` not `call_ai` | unit | `pytest tests/test_generate_exercises.py -x` | Needs update |
| `docs/ai-providers.md` contains `GEMINI_API_KEY` | doc test | `pytest tests/test_ai_provider_docs.py -x` | Wave 0 rewrite |
| `docs/ai-providers.md` contains `gemini-2.0-flash-lite` | doc test | `pytest tests/test_ai_provider_docs.py -x` | Wave 0 rewrite |
| `docs/ai-providers.md` contains `aistudio.google.com` | doc test | `pytest tests/test_ai_provider_docs.py -x` | Wave 0 rewrite |
| Full suite passes after all changes | integration | `pytest` | existing + updated |

### Sampling Rate

- **Per task commit:** `pytest tests/test_ai_provider.py tests/test_ai_provider_docs.py -x`
- **Per wave merge:** `pytest`
- **Phase gate:** Full suite green before verification

### Wave 0 Gaps

- [ ] `tests/test_ai_provider.py` — must be rewritten (all current tests reference removed functions)
- [ ] `tests/test_ai_provider_docs.py` — must be rewritten (all current assertions reference removed strings)
- [ ] `tests/test_generate_exercises.py:test_main_calls_call_ai` — must be updated to assert `call_gemini` is called instead of `call_ai`

---

## Sources

### Primary (HIGH confidence)

- PyPI `google-genai` 1.68.0 — verified version, install command, import path, `Client` API, `generate_content` call, `response.text` (fetched 2026-03-24)
- `scripts/ai_provider.py` — existing code structure, patterns to replicate and remove
- `scripts/generate_exercises.py` — call site structure, `model_config` to simplify
- `tests/test_ai_provider.py` — full test inventory (15+ tests all requiring rewrite)
- `tests/test_ai_provider_docs.py` — full docs test inventory (all assertions need replacement)
- `docs/ai-providers.md` — full current content structure, all strings tested by docs tests
- `plan/config.json` — current field names to remove
- `.github/workflows/daily-content.yml` — current env block to replace
- `requirements.txt` — current packages to remove/add
- `.planning/phases/01-claude-openai-api-key-gemini-api/01-CONTEXT.md` — all locked decisions

### Secondary (MEDIUM confidence)

- PyPI JSON API (`https://pypi.org/pypi/google-genai/json`) — confirmed version 1.68.0 released 2026-03-18

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — version verified against PyPI live on 2026-03-24
- Architecture: HIGH — patterns derived directly from existing codebase and CONTEXT.md locked decisions
- Pitfalls: HIGH — identified from direct code inspection of all files to be changed
- Test strategy: HIGH — existing test patterns observed directly, new patterns follow same conventions

**Research date:** 2026-03-24
**Valid until:** 2026-04-24 (google-genai API is stable; version pin provides isolation)
