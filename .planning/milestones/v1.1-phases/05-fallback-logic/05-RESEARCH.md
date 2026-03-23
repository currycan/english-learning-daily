# Phase 5: Fallback Logic - Research

**Researched:** 2026-03-23
**Domain:** Python exception handling, provider fallback orchestration, unit testing with unittest.mock
**Confidence:** HIGH

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| FALL-01 | 主提供商 API 调用失败时，系统自动切换到备用提供商重试一次 | Implement try/except in call_ai(); compute backup provider from the pair {anthropic, openai} minus primary |
| FALL-02 | 两个提供商均失败时，脚本以非零退出码退出，CI 标红 | call_ai() raises a custom exception; generate_exercises.main() catches it and calls sys.exit(1) |
| FALL-03 | 降级事件写入 CI 日志，包含：使用的提供商、降级原因 | print() to stderr before backup attempt; GitHub Actions captures all stderr as log output |
| TEST-02 | 降级逻辑有单元测试，覆盖主提供商失败 → 自动切换备用提供商的场景 | Extend tests/test_ai_provider.py with two new test functions using unittest.mock |
</phase_requirements>

---

## Summary

Phase 5 adds a single-retry fallback layer to the existing two-provider abstraction built in Phase 4. The architecture is already well-suited: `call_ai()` in `scripts/ai_provider.py` dispatches to `call_claude()` or `call_openai()`, and both low-level callers currently call `sys.exit(1)` on failure. The core change is to stop those low-level callers from exiting and instead surface failures as exceptions that `call_ai()` can catch and redirect to the backup provider.

The fallback ordering is symmetric and already decided: whichever provider is primary, the other is the backup. With only two providers (`{"anthropic", "openai"}`), computing the backup is trivial (`VALID_PROVIDERS - {primary}`). The fallback notice required by FALL-03 is a `print(..., file=sys.stderr)` call before the backup attempt — GitHub Actions streams stderr directly to the CI log, so no additional logging infrastructure is needed.

The test requirements (TEST-02) fit naturally into the existing `tests/test_ai_provider.py` pattern: mock `call_claude` / `call_openai` to raise on first call and succeed on second, then assert the result and that stderr was written.

**Primary recommendation:** Refactor `call_claude()` and `call_openai()` to raise a local `ProviderError` exception instead of calling `sys.exit(1)`. Update `call_ai()` to catch `ProviderError`, log the fallback notice to stderr, then retry with the backup provider. If the backup also raises `ProviderError`, re-raise (or raise a new exception) and let `generate_exercises.main()` handle the final `sys.exit(1)`.

---

## Standard Stack

### Core (all already installed — no new dependencies)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `anthropic` | pinned (Phase 4) | Claude API client | Already in use; `anthropic.APIError` is the specific exception to catch |
| `openai` | pinned (Phase 4) | OpenAI API client | Already in use; bare `Exception` is the current catch target (refine to `openai.APIError` or `openai.OpenAIError`) |
| `pytest` | project standard | Test runner | Existing test suite uses pytest throughout |
| `unittest.mock` | stdlib | Mocking in tests | All Phase 4 tests use `patch` + `MagicMock`; no additional mock library needed |

### No New Dependencies

Phase 5 requires zero new package installations. All functionality is achievable with the existing imports and Python's stdlib `sys` module.

**Installation:**
```bash
# Nothing to install — all dependencies already present
```

---

## Architecture Patterns

### Recommended Change Scope

Only `scripts/ai_provider.py` and `tests/test_ai_provider.py` need modification. `generate_exercises.py` does not need changes unless `call_ai()` is redesigned to propagate exceptions rather than `sys.exit(1)` (see Pattern 2 below).

### Pattern 1: Local Exception + Fallback in call_ai (RECOMMENDED)

**What:** Introduce a module-level `ProviderError` exception. Refactor `call_claude` and `call_openai` to raise `ProviderError` instead of calling `sys.exit(1)`. `call_ai()` catches `ProviderError` from the primary, logs the fallback notice, then calls the backup. If the backup also raises, `call_ai()` calls `sys.exit(1)` (both-fail path).

**When to use:** The interface of `call_ai()` stays identical — callers like `generate_exercises.main()` see no change. The fallback is fully encapsulated in `ai_provider.py`.

**Example structure:**
```python
class ProviderError(Exception):
    """Raised when an AI provider API call fails."""

def call_claude(prompt: str, max_tokens: int = 2048) -> str:
    client = anthropic.Anthropic()
    try:
        response = client.messages.create(...)
        return response.content[0].text
    except anthropic.APIError as e:
        raise ProviderError(f"Claude API call failed: {e}") from e

def call_openai(prompt: str, model: str, max_tokens: int = 2048) -> str:
    client = openai.OpenAI()
    try:
        response = client.chat.completions.create(...)
        return response.choices[0].message.content
    except Exception as e:
        raise ProviderError(f"OpenAI API call failed: {e}") from e

def _backup_provider(primary: str) -> str:
    """Return the other provider. With exactly two providers this is deterministic."""
    return (VALID_PROVIDERS - {primary}).pop()

def call_ai(prompt: str, provider: str, model_config: dict, max_tokens: int = 2048) -> str:
    try:
        return _dispatch(prompt, provider, model_config, max_tokens)
    except ProviderError as primary_err:
        backup = _backup_provider(provider)
        print(
            f"WARNING: Provider '{provider}' failed ({primary_err}). "
            f"Falling back to '{backup}'.",
            file=sys.stderr,
        )
        try:
            return _dispatch(prompt, backup, model_config, max_tokens)
        except ProviderError as backup_err:
            print(f"ERROR: Backup provider '{backup}' also failed: {backup_err}", file=sys.stderr)
            sys.exit(1)
```

### Pattern 2: Preserve sys.exit Behavior in Low-Level Callers (NOT RECOMMENDED)

**What:** Keep `sys.exit(1)` in `call_claude`/`call_openai` and add fallback logic in `generate_exercises.main()` by catching `SystemExit`. This is architecturally messy — catching `SystemExit` is an anti-pattern that makes control flow hard to reason about.

**Why to avoid:** Breaking separation of concerns. Fallback logic belongs in the provider module, not the business logic script.

### Helper: _dispatch private function

Extract the dispatch switch into a private `_dispatch()` helper so `call_ai()` can call it twice (primary, then backup) without duplicating the `if provider == "openai"` branch.

```python
def _dispatch(prompt: str, provider: str, model_config: dict, max_tokens: int) -> str:
    if provider == "openai":
        return call_openai(prompt, model=model_config["openai_model"], max_tokens=max_tokens)
    return call_claude(prompt, max_tokens=max_tokens)
```

### Anti-Patterns to Avoid

- **Catching `SystemExit` for control flow:** Do not catch `SystemExit` to simulate fallback. Refactor to use proper exceptions.
- **Catching bare `Exception` in call_claude:** Phase 4 already fixed this for Claude (`anthropic.APIError` specifically). Prefer `openai.OpenAIError` over bare `Exception` in `call_openai` if available in the installed version (verify at implementation time).
- **Storing fallback state in state.json:** FALL-03 requires CI log output only. No persistent state needed.
- **Multiple retries:** The requirement is exactly one retry with the backup provider. Do not implement retry loops or exponential backoff — that is explicitly out of scope (REQUIREMENTS.md: "Multi-provider load balancing: Overkill for one call/day").

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Logging to CI | Custom logging framework | `print(..., file=sys.stderr)` | GitHub Actions captures stderr natively; no setup required |
| Provider name lookup | Database or config lookup | `VALID_PROVIDERS - {primary}` set arithmetic | Only two providers; set difference is O(1) and self-documenting |
| Retry with backoff | Custom retry decorator | Single manual retry in `call_ai()` | Requirements specify exactly one retry; more complexity is out of scope |

**Key insight:** The entire fallback mechanism is ~15 lines of Python in one function. Any abstraction beyond what the requirements specify adds complexity with no benefit for a one-call-per-day system.

---

## Common Pitfalls

### Pitfall 1: call_claude / call_openai Still Exit on Error After Refactor

**What goes wrong:** If `sys.exit(1)` is left in either low-level caller, `call_ai()` can never catch the error — `SystemExit` propagates past `except ProviderError`.
**Why it happens:** Incremental refactor leaves old exit path in place.
**How to avoid:** Replace every `sys.exit(1)` in `call_claude` and `call_openai` with `raise ProviderError(...)`. Run existing tests first — `test_call_claude_exits_on_api_error` and `test_call_openai_exits_on_error` will break, which is expected. Update those tests to assert `ProviderError` is raised instead.
**Warning signs:** Tests that previously checked for `SystemExit` now pass when they should fail.

### Pitfall 2: Existing Tests Break Without Update

**What goes wrong:** Three existing tests assert `SystemExit` from `call_claude` / `call_openai` directly: `test_call_claude_exits_on_api_error`, `test_call_openai_exits_on_error`. After refactor these will fail.
**Why it happens:** The refactor changes the contract of these functions.
**How to avoid:** Update existing tests in the same commit/plan as the implementation change. New assertion: `pytest.raises(ProviderError)` rather than `pytest.raises(SystemExit)`.

### Pitfall 3: Fallback Calls Itself (Infinite Loop)

**What goes wrong:** If the backup provider string is computed incorrectly and equals the primary, `call_ai()` retries the same failing provider.
**Why it happens:** Set arithmetic bug or typo in provider name.
**How to avoid:** Assert in `_backup_provider()` that the returned string differs from the primary. With only two providers, `(VALID_PROVIDERS - {primary}).pop()` is deterministic. Add a test asserting `_backup_provider("anthropic") == "openai"` and vice versa.

### Pitfall 4: model_config Missing openai_model Key During Fallback

**What goes wrong:** When anthropic is primary and openai is the backup, `call_ai()` calls `call_openai()` during fallback — but `model_config["openai_model"]` must be present. If the caller passes an incomplete `model_config`, this raises a `KeyError`.
**Why it happens:** `generate_exercises.main()` already constructs `model_config = {"openai_model": config.get("openai_model", "gpt-4o-mini")}` correctly, so this is not a real risk in production. But tests that call `call_ai()` directly must pass a complete `model_config`.
**How to avoid:** Ensure all `call_ai()` test invocations include `model_config={"openai_model": "gpt-4o-mini"}`. Document in the function docstring that `model_config` must always contain `openai_model`.

### Pitfall 5: FALL-03 Log Not Visible if Output Goes to stdout

**What goes wrong:** Fallback notice is printed to stdout instead of stderr. In the CI pipeline (`generate_exercises.py | push_bark.py`), stdout is piped to the next process, so a fallback notice on stdout corrupts the Markdown output.
**Why it happens:** Missing `file=sys.stderr` argument.
**How to avoid:** Always pass `file=sys.stderr` in the fallback `print()` call. Verify in tests using `capsys.readouterr()`.

---

## Code Examples

### Verified Pattern: Raising Instead of Exiting

```python
# Pattern consistent with project immutability and error handling conventions
def call_claude(prompt: str, max_tokens: int = 2048) -> str:
    client = anthropic.Anthropic()
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

### Verified Pattern: Testing Fallback with unittest.mock

```python
# TEST-02: primary fails, backup succeeds
def test_call_ai_fallback_primary_fails_backup_succeeds():
    with patch("scripts.ai_provider.call_claude") as mock_claude, \
         patch("scripts.ai_provider.call_openai") as mock_openai:
        from scripts.ai_provider import ProviderError
        mock_claude.side_effect = ProviderError("claude down")
        mock_openai.return_value = "openai response"
        result = ap.call_ai("prompt", provider="anthropic", model_config={"openai_model": "gpt-4o-mini"})
    assert result == "openai response"
    mock_openai.assert_called_once()

# TEST-02: both fail
def test_call_ai_fallback_both_fail_exits():
    with patch("scripts.ai_provider.call_claude") as mock_claude, \
         patch("scripts.ai_provider.call_openai") as mock_openai:
        from scripts.ai_provider import ProviderError
        mock_claude.side_effect = ProviderError("claude down")
        mock_openai.side_effect = ProviderError("openai down")
        with pytest.raises(SystemExit) as exc_info:
            ap.call_ai("prompt", provider="anthropic", model_config={"openai_model": "gpt-4o-mini"})
    assert exc_info.value.code == 1

# TEST-02: fallback notice appears in stderr
def test_call_ai_fallback_logs_to_stderr(capsys):
    with patch("scripts.ai_provider.call_claude") as mock_claude, \
         patch("scripts.ai_provider.call_openai") as mock_openai:
        from scripts.ai_provider import ProviderError
        mock_claude.side_effect = ProviderError("claude down")
        mock_openai.return_value = "ok"
        ap.call_ai("prompt", provider="anthropic", model_config={"openai_model": "gpt-4o-mini"})
    captured = capsys.readouterr()
    assert "anthropic" in captured.err
    assert "openai" in captured.err
```

### Verified Pattern: Updating Existing Tests After Refactor

```python
# BEFORE (Phase 4 — call_claude exits directly):
def test_call_claude_exits_on_api_error():
    ...
    with pytest.raises(SystemExit) as exc_info:
        ap.call_claude("prompt")
    assert exc_info.value.code == 1

# AFTER (Phase 5 — call_claude raises ProviderError):
def test_call_claude_raises_provider_error_on_api_error():
    ...
    with pytest.raises(ap.ProviderError):
        ap.call_claude("prompt")
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `sys.exit(1)` in low-level callers | Raise `ProviderError`; exit only in `call_ai()` on both-fail | Phase 5 | Enables testable fallback without mocking `sys.exit` |
| `call_ai()` is a thin dispatcher | `call_ai()` is fallback orchestrator | Phase 5 | Single responsibility for retry lives in one function |

**Deprecated/outdated after Phase 5:**
- `sys.exit(1)` inside `call_claude()` and `call_openai()`: replaced by `raise ProviderError`.
- Tests asserting `SystemExit` from low-level callers: updated to assert `ProviderError`.

---

## Open Questions

1. **Should `openai.OpenAIError` replace bare `Exception` in `call_openai`?**
   - What we know: Phase 4 used bare `Exception` for OpenAI. `anthropic.APIError` is used specifically for Claude.
   - What's unclear: Whether the installed `openai` package version exposes `openai.OpenAIError` as a reliable base class.
   - Recommendation: At implementation time, verify with `import openai; print(openai.OpenAIError)`. If available, prefer it over bare `Exception` for consistency with the Claude pattern. If not, bare `Exception` is acceptable with a comment explaining the asymmetry.

2. **Should the fallback notice include the full exception message?**
   - What we know: FALL-03 requires provider name and fallback reason. The exception message is the natural source of the reason.
   - Recommendation: Include `str(primary_err)` in the fallback notice — it satisfies FALL-03 and provides actionable CI log output.

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (existing) |
| Config file | `pytest.ini` (pythonpath = .) |
| Quick run command | `pytest tests/test_ai_provider.py -x` |
| Full suite command | `pytest` |

### Phase Requirements to Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| FALL-01 | Primary fails, backup succeeds, returns backup result | unit | `pytest tests/test_ai_provider.py::test_call_ai_fallback_primary_fails_backup_succeeds -x` | Wave 0 (new test) |
| FALL-01 | Symmetric: openai primary fails, anthropic backup succeeds | unit | `pytest tests/test_ai_provider.py::test_call_ai_fallback_openai_primary_fails -x` | Wave 0 (new test) |
| FALL-02 | Both fail, sys.exit(1) | unit | `pytest tests/test_ai_provider.py::test_call_ai_fallback_both_fail_exits -x` | Wave 0 (new test) |
| FALL-03 | Fallback notice written to stderr with provider names | unit | `pytest tests/test_ai_provider.py::test_call_ai_fallback_logs_to_stderr -x` | Wave 0 (new test) |
| TEST-02 | All above unit tests passing | unit | `pytest tests/test_ai_provider.py -x` | Wave 0 (extends existing file) |

### Sampling Rate

- **Per task commit:** `pytest tests/test_ai_provider.py -x`
- **Per wave merge:** `pytest`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps

- [ ] New test functions in `tests/test_ai_provider.py` — covers FALL-01, FALL-02, FALL-03
- [ ] Update existing tests (`test_call_claude_exits_on_api_error`, `test_call_openai_exits_on_error`) to assert `ProviderError` instead of `SystemExit`

*(No new files needed — extends existing `tests/test_ai_provider.py`)*

---

## Sources

### Primary (HIGH confidence)

- Direct code inspection: `scripts/ai_provider.py` — full interface, existing exception handling, `VALID_PROVIDERS` set
- Direct code inspection: `tests/test_ai_provider.py` — existing mock patterns and test conventions
- Direct code inspection: `scripts/generate_exercises.py` — call sites and `main()` error contract
- `.planning/STATE.md` — "Fallback ordering: configured provider first → other provider (symmetric)" decision locked in Phase 4
- `.planning/REQUIREMENTS.md` — FALL-01, FALL-02, FALL-03, TEST-02 definitions

### Secondary (MEDIUM confidence)

- Python `unittest.mock` stdlib documentation — `patch`, `side_effect`, `MagicMock` patterns verified against existing test usage in project
- GitHub Actions documentation — stderr from Python scripts is captured in CI job log automatically (standard behavior, no configuration needed)

### Tertiary (LOW confidence — not needed, requirements are clear)

- None required; all findings are grounded in direct code inspection and confirmed project decisions.

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — zero new dependencies; all tools already in use
- Architecture: HIGH — single change location (`ai_provider.py`), pattern directly grounded in existing code structure and STATE.md locked decisions
- Pitfalls: HIGH — derived from direct code inspection of existing test assertions and Python exception semantics
- Test patterns: HIGH — all test patterns copied from existing Phase 4 tests in same file

**Research date:** 2026-03-23
**Valid until:** 2026-06-23 (stable stdlib + anthropic/openai client APIs)
