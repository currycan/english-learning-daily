# Phase 4: Provider Abstraction + OpenAI Integration - Research

**Researched:** 2026-03-23
**Domain:** Python multi-provider AI client abstraction, OpenAI SDK integration
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Prompt Strategy**
- Single shared prompt for both providers — same `build_prompt()` output sent to whichever provider is active
- No provider-specific prompt tuning; output format consistency guaranteed by prompt rules, not by tailoring

**Config Schema**
- Add two top-level fields to `plan/config.json`:
  - `"ai_provider": "anthropic"` — default provider; overridden by `AI_PROVIDER` env var at runtime
  - `"openai_model": "gpt-4o-mini"` — OpenAI model; configurable, defaults to gpt-4o-mini
- Claude model (`claude-haiku-4-5-20251001`) stays hardcoded in source — not moved to config
- New config fields sit at the same level as `content_feeds`, `timezone`

**Provider Resolution**
- Priority: `AI_PROVIDER` env var (if set and non-empty) overrides `ai_provider` from config.json
- Resolution happens once at script entry, passed into the generation function

**Error Handling for Invalid Provider**
- If `AI_PROVIDER` or `ai_provider` config resolves to an unknown value (not `"anthropic"` or `"openai"`): `sys.exit(1)` with a clear stderr message listing valid values
- No silent defaulting — misconfiguration must be visible

**OpenAI Client Pattern**
- `openai.OpenAI()` instantiated inside the call function (same pattern as `anthropic.Anthropic()` inside `call_claude()`) — keeps patching clean in tests
- Response extraction: `response.choices[0].message.content`

**CI Workflow Changes**
- `daily-content.yml` env block: add `OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}` alongside existing `ANTHROPIC_API_KEY`
- `AI_PROVIDER` is NOT added to yml env — provider selection is controlled via `plan/config.json`, no yml changes needed when switching
- Missing/unused API key (e.g., OPENAI_API_KEY is empty when provider=anthropic) is fine — only the active provider's key is used

**Module Structure**
- New file `scripts/ai_provider.py` encapsulates provider selection, both `call_claude()` and `call_openai()`, and a unified `call_ai(prompt, provider, model_config)` dispatcher
- `generate_exercises.py` imports from `ai_provider.py` instead of calling `anthropic` directly
- `build_prompt()`, `parse_response()`, `render_markdown()` stay in `generate_exercises.py` unchanged

### Claude's Discretion
- Exact function signatures inside `ai_provider.py`
- How `model_config` is passed (dict slice vs individual args)
- Whether to use a single `call_ai()` or keep `call_claude()` / `call_openai()` as named functions dispatched by a wrapper

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| PRVD-01 | System calls AI through a unified interface; business logic is decoupled from specific provider | `call_ai()` dispatcher in `scripts/ai_provider.py` with `call_claude()` / `call_openai()` behind it |
| PRVD-02 | User can switch provider via `AI_PROVIDER=openai\|anthropic` env var (runtime priority) | Env var read with `os.environ.get("AI_PROVIDER")`, checked before config; `sys.exit(1)` on unknown value |
| PRVD-03 | User can set `ai_provider` default in `plan/config.json`; env var takes priority | Config loaded by existing `json.loads(Path(...).read_text())` pattern; env var checked first |
| OAPI-01 | System uses OpenAI gpt-4o-mini to generate content identical in format to current output | `client.chat.completions.create(model=..., messages=[{"role":"user","content":prompt}])` returns text via `response.choices[0].message.content`; same `parse_response()` validates it |
| OAPI-02 | OpenAI model is configurable via `plan/config.json` (default `gpt-4o-mini`) | `openai_model` field read from config, passed into `call_ai()` via `model_config` dict |
| OAPI-03 | `OPENAI_API_KEY` only from env / GitHub Secrets; never in source or config files | `openai.OpenAI()` reads key automatically from `OPENAI_API_KEY` env var; no explicit key param needed |
| TEST-01 | Unit tests for OpenAI provider path, API calls mocked | `patch("scripts.ai_provider.openai.OpenAI")` pattern verified; `MagicMock` chain for `mock_client.chat.completions.create.return_value` |
</phase_requirements>

---

## Summary

Phase 4 introduces a new `scripts/ai_provider.py` module that encapsulates all AI-provider logic, allowing `generate_exercises.py` to call a single `call_ai()` dispatcher instead of `call_claude()` directly. The OpenAI SDK (v2.x, currently 2.29.0) follows the same instantiate-inside-function pattern already used for the Anthropic client, making it straightforward to mock in tests. Both clients read their respective API keys automatically from environment variables (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`); no key handling is needed in application code.

Provider resolution is a two-level lookup: env var `AI_PROVIDER` takes priority over the `ai_provider` field in `plan/config.json`. Any value that is neither `"anthropic"` nor `"openai"` must cause `sys.exit(1)` with a clear stderr message. This phase also fixes a documented tech debt item: `call_claude()` currently catches bare `Exception`; the refactored version must catch `anthropic.APIError` (the correct base class in the anthropic SDK hierarchy).

The test surface is narrow and well-defined: mock the `openai.OpenAI` constructor in `scripts.ai_provider`, configure the mock's `chat.completions.create` return value, assert the text is returned and the process exits 1 on API failures. The existing `test_generate_exercises.py` pattern (`patch("scripts.generate_exercises.anthropic.Anthropic")`) is the exact model to follow.

**Primary recommendation:** Create `scripts/ai_provider.py` with `call_claude()`, `call_openai()`, `call_ai()`, and `resolve_provider()`; update `generate_exercises.py:main()` to call `call_ai()`; add `openai` to `requirements.txt`; add `OPENAI_API_KEY` secret reference to the CI workflow.

---

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `anthropic` | 0.86.0 (pinned in requirements.txt) | Claude API client | Already in use; `anthropic.Anthropic()` instantiation pattern established |
| `openai` | 2.29.0 (latest as of 2026-03-17) | OpenAI API client | Official SDK; reads `OPENAI_API_KEY` from env automatically; same sync client pattern as anthropic |
| `pytest` | 8.3.5 (pinned) | Test framework | Already in use; `unittest.mock.patch` works with both SDKs |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `unittest.mock` | stdlib | Patching AI clients in tests | Always — never make live API calls in tests |
| `os` | stdlib | Reading `AI_PROVIDER` env var | Provider resolution in `resolve_provider()` |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `openai.OpenAI()` | `litellm` or `langchain` | Both add heavy dependencies; not needed when only two providers are supported |
| `unittest.mock.patch` | `pytest-mock` | `pytest-mock` is syntactic sugar; `unittest.mock` is already used in the codebase |

**Installation:**
```bash
pip install openai==2.29.0
```
Add to `requirements.txt`: `openai==2.29.0`

---

## Architecture Patterns

### Recommended Project Structure

New file to create:
```
scripts/
├── ai_provider.py        # NEW: provider selection + call_claude / call_openai / call_ai
├── generate_exercises.py # MODIFY: remove call_claude import/usage, import call_ai + resolve_provider
└── ...                   # all other scripts unchanged
```

New test file to create:
```
tests/
├── test_ai_provider.py   # NEW: unit tests for OpenAI path, error handling, provider resolution
└── ...                   # existing tests unchanged
```

### Pattern 1: Client-Inside-Function (established convention)

**What:** Instantiate the AI client inside the call function, not at module level.
**When to use:** Always for both `call_claude()` and `call_openai()` — this is the existing codebase convention explicitly documented in STATE.md and CONTEXT.md.
**Why:** Makes `patch("scripts.ai_provider.openai.OpenAI")` work correctly; no module-level state.

```python
# Source: existing scripts/generate_exercises.py pattern + codebase convention
def call_openai(prompt: str, model: str, max_tokens: int = 2048) -> str:
    """Call OpenAI API. Returns response text. Exits 1 on any error."""
    client = openai.OpenAI()  # reads OPENAI_API_KEY from env automatically
    try:
        response = client.chat.completions.create(
            model=model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"ERROR: OpenAI API call failed: {e}", file=sys.stderr)
        sys.exit(1)
```

### Pattern 2: Provider Resolution with Env-Over-Config Priority

**What:** Resolve provider once, fail fast on unknown values.
**When to use:** At the top of `main()` in `generate_exercises.py`, before any API call.

```python
# Source: CONTEXT.md locked decisions + codebase error handling convention
VALID_PROVIDERS = {"anthropic", "openai"}

def resolve_provider(config: dict) -> str:
    """Resolve AI provider. Env var AI_PROVIDER takes priority over config.ai_provider."""
    provider = os.environ.get("AI_PROVIDER") or config.get("ai_provider", "anthropic")
    if provider not in VALID_PROVIDERS:
        print(
            f"ERROR: Unknown AI provider '{provider}'. Valid: {sorted(VALID_PROVIDERS)}",
            file=sys.stderr,
        )
        sys.exit(1)
    return provider
```

### Pattern 3: Unified Dispatcher

**What:** `call_ai()` routes to `call_claude()` or `call_openai()` based on resolved provider.
**When to use:** `generate_exercises.py:main()` calls `call_ai()` instead of `call_claude()` directly.

```python
# Source: CONTEXT.md locked decisions
CLAUDE_MODEL = "claude-haiku-4-5-20251001"  # stays hardcoded per decision

def call_ai(prompt: str, provider: str, model_config: dict, max_tokens: int = 2048) -> str:
    """Dispatch to the active AI provider. provider must be 'anthropic' or 'openai'."""
    if provider == "openai":
        return call_openai(prompt, model=model_config["openai_model"], max_tokens=max_tokens)
    return call_claude(prompt, max_tokens=max_tokens)
```

`model_config` is a dict slice from the loaded config, e.g. `{"openai_model": config.get("openai_model", "gpt-4o-mini")}`.

### Pattern 4: Fixing the Tech Debt — Specific Exception in call_claude

**What:** Replace bare `except Exception` with `except anthropic.APIError`.
**Why:** Documented tech debt in STATE.md; `anthropic.APIError` is the correct base class covering `APIStatusError`, `APIConnectionError`, and `APITimeoutError`.

```python
# Before (tech debt):
except Exception as e:

# After (correct):
except anthropic.APIError as e:
```

### Anti-Patterns to Avoid
- **Module-level client instantiation:** `client = openai.OpenAI()` at top of file breaks `patch()` in tests.
- **Hardcoded API keys:** Never pass `api_key=` parameter to `openai.OpenAI()` in application code; the SDK reads from env automatically.
- **Silent provider defaulting:** If `AI_PROVIDER=foobar`, the script must exit 1, not fall back silently.
- **Provider selection inside config loading:** Resolve provider in `main()`, not inside `load_config()` — keeps config loading pure.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| OpenAI HTTP client | Custom `requests` calls to `api.openai.com` | `openai.OpenAI()` | SDK handles auth, retries, response model deserialization, error hierarchy |
| API key injection | Manual env var read + constructor arg | `openai.OpenAI()` with no args | SDK automatically reads `OPENAI_API_KEY` from env; explicit key risks accidental logging |
| Response parsing | Custom dict parsing of `choices[0]` | `response.choices[0].message.content` | SDK returns typed Pydantic models; attribute access is safe |

---

## Common Pitfalls

### Pitfall 1: Wrong Patch Target for OpenAI Client
**What goes wrong:** Test patches `openai.OpenAI` globally, but the test catches the wrong import binding.
**Why it happens:** Python's mock patches the name in the module where it is used, not where it is defined.
**How to avoid:** Patch `"scripts.ai_provider.openai.OpenAI"` — the module that imports and instantiates it.
**Warning signs:** Mock is configured but the real API is still called (or `ModuleNotFoundError` on `openai`).

Correct pattern (mirrors existing `test_generate_exercises.py`):
```python
with patch("scripts.ai_provider.openai.OpenAI") as MockOpenAI:
    mock_client = MagicMock()
    MockOpenAI.return_value = mock_client
    mock_client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content='{"vocabulary":...}'))]
    )
```

### Pitfall 2: Config Loading Breaks Other Scripts
**What goes wrong:** Adding `ai_provider` and `openai_model` to `plan/config.json` breaks scripts that load the same file if they don't tolerate unknown keys.
**Why it happens:** Scripts use `config["content_feeds"]` etc. by key; new top-level keys are harmless unless something iterates and rejects unknown fields.
**How to avoid:** All existing config loaders use direct key access, not schema validation — new fields are transparent. Verify by checking `feed_article.py` config usage (reads only `content_feeds`; no schema enforcement).
**Warning signs:** Existing tests fail after adding fields to `plan/config.json`.

### Pitfall 3: OPENAI_API_KEY Absent in Tests
**What goes wrong:** `openai.OpenAI()` raises `openai.OpenAIError: No API key` even in tests when the env var is not set.
**Why it happens:** The SDK validates the API key at instantiation time in some versions.
**How to avoid:** Since `openai.OpenAI` is patched entirely in unit tests, the real constructor is never called — the mock client is returned instead. No env var needed in tests. Confirm with a sanity-check test that the mock intercepts instantiation.

### Pitfall 4: max_tokens Parameter Name Difference
**What goes wrong:** Passing `max_tokens` to the OpenAI chat completions endpoint may differ from Anthropic's parameter.
**Why it happens:** As of OpenAI SDK v1+, `max_tokens` is valid for `chat.completions.create`. No rename needed.
**How to avoid:** Use `max_tokens=2048` — same parameter name works for both providers.

### Pitfall 5: call_claude Still Referenced After Refactor
**What goes wrong:** `generate_exercises.py` still imports `call_claude` directly from itself after refactor, causing duplicate definitions.
**How to avoid:** After moving `call_claude` to `ai_provider.py`, remove it entirely from `generate_exercises.py`. Only `call_ai` is imported.

---

## Code Examples

Verified patterns from official sources and existing codebase:

### OpenAI Chat Completions Call
```python
# Source: PyPI openai 2.29.0 README / platform.openai.com
import openai

def call_openai(prompt: str, model: str, max_tokens: int = 2048) -> str:
    client = openai.OpenAI()  # reads OPENAI_API_KEY from env
    try:
        response = client.chat.completions.create(
            model=model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"ERROR: OpenAI API call failed: {e}", file=sys.stderr)
        sys.exit(1)
```

### Mocking OpenAI in Tests
```python
# Source: verified pattern from openai-python issues + existing test_generate_exercises.py convention
from unittest.mock import patch, MagicMock
import pytest
import scripts.ai_provider as ap

def test_call_openai_returns_content():
    with patch("scripts.ai_provider.openai.OpenAI") as MockOpenAI:
        mock_client = MagicMock()
        MockOpenAI.return_value = mock_client
        mock_client.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content='{"vocabulary": [], "chunks": [], "questions": []}'))]
        )
        result = ap.call_openai("test prompt", model="gpt-4o-mini")
    assert result == '{"vocabulary": [], "chunks": [], "questions": []}'

def test_call_openai_exits_on_error():
    with patch("scripts.ai_provider.openai.OpenAI") as MockOpenAI:
        mock_client = MagicMock()
        MockOpenAI.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API error")
        with pytest.raises(SystemExit) as exc_info:
            ap.call_openai("test prompt", model="gpt-4o-mini")
    assert exc_info.value.code == 1
```

### Provider Resolution
```python
# Source: CONTEXT.md locked decisions + codebase convention (CONVENTIONS.md)
import os
import sys

VALID_PROVIDERS = {"anthropic", "openai"}

def resolve_provider(config: dict) -> str:
    provider = os.environ.get("AI_PROVIDER") or config.get("ai_provider", "anthropic")
    if provider not in VALID_PROVIDERS:
        print(
            f"ERROR: Unknown AI provider '{provider}'. Valid: {sorted(VALID_PROVIDERS)}",
            file=sys.stderr,
        )
        sys.exit(1)
    return provider
```

### Updated generate_exercises.py main()
```python
# Source: CONTEXT.md integration point spec
def main() -> None:
    raw = sys.stdin.read()
    try:
        envelope = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON from stdin: {e}", file=sys.stderr)
        sys.exit(1)

    config = load_config()  # loads plan/config.json
    provider = resolve_provider(config)
    model_config = {"openai_model": config.get("openai_model", "gpt-4o-mini")}

    prompt = build_prompt(envelope)
    raw_response = call_ai(prompt, provider=provider, model_config=model_config)
    exercises = parse_response(raw_response)
    markdown = render_markdown(envelope, exercises)
    print(markdown)
```

### Updated plan/config.json Schema
```json
{
  "morning_hour": 7,
  "evening_hour": 21,
  "weekly_recording_day": "saturday",
  "timezone": "Asia/Shanghai",
  "ai_provider": "anthropic",
  "openai_model": "gpt-4o-mini",
  "content_feeds": {
    "primary_url": "...",
    "fallback_url": "...",
    "content_topics": [...]
  }
}
```

### CI Workflow Addition (daily-content.yml)
```yaml
# Add to the existing env block in generate-content job
env:
  ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `openai` v0.x (`openai.ChatCompletion.create()`) | `openai` v1+: `client.chat.completions.create()` | Nov 2023 (v1.0.0) | Must use client-based API; old module-level calls are removed |
| `except Exception` in call_claude | `except anthropic.APIError` | Phase 4 (tech debt fix) | Catches only API errors, not programming errors |

**Deprecated/outdated:**
- `openai.ChatCompletion.create()`: Removed in v1.0.0; replaced by `client.chat.completions.create()`
- `openai.api_key = "..."` global assignment: Replaced by `openai.OpenAI(api_key=...)` or env var; do not use

---

## Open Questions

1. **config.json loading in generate_exercises.py**
   - What we know: `generate_exercises.py` currently has no config loading — it reads only from stdin (article envelope)
   - What's unclear: Where does `load_config()` live? Other scripts (e.g., `content_utils.py`) may already have one
   - Recommendation: Check `scripts/content_utils.py` or similar for an existing `load_config()` helper. If none exists, add a small private helper inside `generate_exercises.py` that reads `plan/config.json` using `Path` — consistent with `plan_state.py:load_state()` pattern. Do NOT add a new public function to `ai_provider.py` for config loading (single responsibility).

2. **anthropic.APIError scope of change**
   - What we know: Fixing `except Exception` → `except anthropic.APIError` is documented tech debt (STATE.md)
   - What's unclear: The fix touches `call_claude()` which moves to `ai_provider.py`; the change happens naturally during the refactor
   - Recommendation: Make the fix in the new `ai_provider.py:call_claude()` — no need for a separate task.

---

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 8.3.5 |
| Config file | none (pytest discovers `tests/` automatically) |
| Quick run command | `pytest tests/test_ai_provider.py -x` |
| Full suite command | `pytest` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| PRVD-01 | `call_ai()` dispatches to correct provider | unit | `pytest tests/test_ai_provider.py::test_call_ai_dispatches_anthropic -x` | Wave 0 |
| PRVD-01 | `call_ai()` dispatches to openai when provider=openai | unit | `pytest tests/test_ai_provider.py::test_call_ai_dispatches_openai -x` | Wave 0 |
| PRVD-02 | `resolve_provider()` uses env var when set | unit | `pytest tests/test_ai_provider.py::test_resolve_provider_env_var_priority -x` | Wave 0 |
| PRVD-02 | `resolve_provider()` exits 1 on unknown provider | unit | `pytest tests/test_ai_provider.py::test_resolve_provider_unknown_exits -x` | Wave 0 |
| PRVD-03 | `resolve_provider()` falls back to config.ai_provider | unit | `pytest tests/test_ai_provider.py::test_resolve_provider_config_default -x` | Wave 0 |
| OAPI-01 | `call_openai()` returns content from response | unit | `pytest tests/test_ai_provider.py::test_call_openai_returns_content -x` | Wave 0 |
| OAPI-01 | `call_openai()` exits 1 on API error | unit | `pytest tests/test_ai_provider.py::test_call_openai_exits_on_error -x` | Wave 0 |
| OAPI-02 | `call_openai()` passes model from model_config | unit | `pytest tests/test_ai_provider.py::test_call_openai_uses_configured_model -x` | Wave 0 |
| OAPI-03 | No API key in source or config files | manual | grep audit of source + config.json | N/A |
| TEST-01 | All OpenAI path tests pass with mocked API | unit | `pytest tests/test_ai_provider.py -x` | Wave 0 |

### Sampling Rate
- **Per task commit:** `pytest tests/test_ai_provider.py -x`
- **Per wave merge:** `pytest`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_ai_provider.py` — covers PRVD-01, PRVD-02, PRVD-03, OAPI-01, OAPI-02, TEST-01
- [ ] `scripts/ai_provider.py` — the module under test must exist before tests can be written

*(Existing test infrastructure is complete; only the new module and its test file are missing.)*

---

## Sources

### Primary (HIGH confidence)
- PyPI `openai` 2.29.0 — latest version, basic usage, env var key loading
- `github.com/openai/openai-python` README — `client.chat.completions.create()` pattern, `response.choices[0].message.content`
- Existing `scripts/generate_exercises.py` — `call_claude()` pattern, instantiate-inside-function convention
- Existing `tests/test_generate_exercises.py` — `patch("scripts.generate_exercises.anthropic.Anthropic")` mock pattern
- `.planning/codebase/CONVENTIONS.md` — UPPER_CASE constants, `sys.exit(1)` + stderr pattern, type hints
- `.planning/phases/04-provider-abstraction-openai-integration/04-CONTEXT.md` — all locked decisions

### Secondary (MEDIUM confidence)
- WebSearch + multiple community sources — correct patch target for `openai.OpenAI` in unittest (verified by cross-checking with existing codebase pattern for anthropic)
- `docs.anthropic.com/en/api/errors` — `anthropic.APIError` exception hierarchy (WebSearch verified against pypi.org/project/anthropic)

### Tertiary (LOW confidence)
- None

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — official PyPI versions confirmed; API pattern confirmed from official README
- Architecture: HIGH — all decisions locked in CONTEXT.md; patterns verified against existing codebase
- Pitfalls: HIGH — patch target pitfall verified against existing test file pattern in this codebase
- Test map: HIGH — test framework already in use; only new file needed

**Research date:** 2026-03-23
**Valid until:** 2026-04-23 (openai SDK moves fast; verify version before pinning)
