---
phase: 05-fallback-logic
verified: 2026-03-23T12:00:00+08:00
status: passed
score: 5/5 must-haves verified
re_verification: false
---

# Phase 5: Fallback Logic Verification Report

**Phase Goal:** Implement automatic provider fallback so the system retries with the backup provider when the primary fails, without user intervention.
**Verified:** 2026-03-23T12:00:00+08:00
**Status:** passed
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| #  | Truth                                                                                                       | Status     | Evidence                                                                                                     |
|----|-------------------------------------------------------------------------------------------------------------|------------|--------------------------------------------------------------------------------------------------------------|
| 1  | When the primary provider raises an API error, call_ai() retries once with the backup provider and returns its result | ✓ VERIFIED | `call_ai` wraps `_dispatch` in try/except ProviderError → logs WARNING → calls `_dispatch(backup, ...)`. Tests `test_call_ai_fallback_primary_fails_backup_succeeds` and `test_call_ai_fallback_openai_primary_fails` both pass. |
| 2  | When both providers fail, call_ai() exits with code 1 (CI job fails)                                       | ✓ VERIFIED | Inner except catches backup ProviderError → `sys.exit(1)` at line 120. Test `test_call_ai_fallback_both_fail_exits` passes asserting `exc_info.value.code == 1`. |
| 3  | The fallback notice on stderr names the failed provider and the reason before the backup attempt             | ✓ VERIFIED | `print(f"WARNING: Provider '{provider}' failed ({primary_err}). Falling back to '{backup}'.", file=sys.stderr)` at line 108–112. Test `test_call_ai_fallback_logs_to_stderr` confirms "anthropic" and "openai" appear in captured.err. |
| 4  | call_claude() and call_openai() raise ProviderError on failure, not sys.exit(1)                             | ✓ VERIFIED | `call_claude` raises `ProviderError` at line 53; `call_openai` raises `ProviderError` at line 72. Neither contains sys.exit. Tests `test_call_claude_raises_provider_error_on_api_error` and `test_call_openai_raises_provider_error_on_error` pass. |
| 5  | All existing provider tests pass alongside new fallback tests                                                | ✓ VERIFIED | `pytest tests/test_ai_provider.py` → 17/17 passed; `pytest` (full suite) → 108/108 passed.                 |

**Score:** 5/5 truths verified

---

### Required Artifacts

| Artifact                         | Expected                                                                             | Status     | Details                                                                                                       |
|----------------------------------|--------------------------------------------------------------------------------------|------------|---------------------------------------------------------------------------------------------------------------|
| `tests/test_ai_provider.py`      | Unit tests for FALL-01, FALL-02, FALL-03, TEST-02; updated SystemExit → ProviderError assertions; contains `test_call_ai_fallback_primary_fails_backup_succeeds` | ✓ VERIFIED | File exists, 173 lines. All six new fallback tests present. Renamed tests confirmed. Old names `test_call_claude_exits_on_api_error` and `test_call_openai_exits_on_error` absent. |
| `scripts/ai_provider.py`         | ProviderError exception, `_backup_provider()`, `_dispatch()`, fallback-aware `call_ai()`; contains `class ProviderError` | ✓ VERIFIED | File exists, 121 lines. `class ProviderError(Exception)` at line 26. `_backup_provider` at line 75. `_dispatch` at line 80. `call_ai` fallback chain at lines 104–120. |

---

### Key Link Verification

| From                                  | To                              | Via                                        | Status     | Details                                                                                              |
|---------------------------------------|---------------------------------|--------------------------------------------|------------|------------------------------------------------------------------------------------------------------|
| `scripts/ai_provider.py::call_ai`     | `scripts/ai_provider.py::_dispatch` | `try/except ProviderError → _dispatch(backup, ...)` | ✓ WIRED    | Primary call at line 105; backup call at line 114 inside except block. Pattern `_dispatch(prompt, backup` confirmed at line 114. |
| `scripts/ai_provider.py::call_ai`     | `sys.stderr`                    | `print(..., file=sys.stderr)`              | ✓ WIRED    | Lines 108–112 (WARNING before backup attempt) and 116–119 (ERROR after both fail). Both use `file=sys.stderr`. |

---

### Requirements Coverage

| Requirement | Source Plan | Description                                                                       | Status      | Evidence                                                                                              |
|-------------|-------------|-----------------------------------------------------------------------------------|-------------|-------------------------------------------------------------------------------------------------------|
| FALL-01     | 05-01-PLAN  | 主提供商 API 调用失败时，系统自动切换到备用提供商重试一次                          | ✓ SATISFIED | `call_ai` catches ProviderError from primary, calls `_dispatch` with backup provider. Test passes.   |
| FALL-02     | 05-01-PLAN  | 两个提供商均失败时，脚本以非零退出码退出，CI 标红                                 | ✓ SATISFIED | `sys.exit(1)` called only after backup ProviderError. Test `test_call_ai_fallback_both_fail_exits` asserts code==1. |
| FALL-03     | 05-01-PLAN  | 降级事件写入 CI 日志，包含：使用的提供商、降级原因                                 | ✓ SATISFIED | WARNING message includes provider name and error reason before backup attempt; ERROR message after both fail. Both go to stderr (CI log). |
| TEST-02     | 05-01-PLAN  | 降级逻辑有单元测试，覆盖主提供商失败 → 自动切换备用提供商的场景                   | ✓ SATISFIED | `test_call_ai_fallback_primary_fails_backup_succeeds`, `test_call_ai_fallback_openai_primary_fails`, `test_call_ai_fallback_both_fail_exits`, `test_call_ai_fallback_logs_to_stderr`, plus two `_backup_provider` unit tests. |

No orphaned requirements: REQUIREMENTS.md maps FALL-01, FALL-02, FALL-03, TEST-02 to Phase 5, and all four are covered by plan 05-01.

---

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| — | — | — | — | No anti-patterns found |

Notes:
- No TODO/FIXME/HACK/PLACEHOLDER comments in either modified file.
- No empty return values (`return null`, `return []`, `return {}`).
- `sys.exit(1)` appears three times: line 38 (`resolve_provider`, correct — invalid provider config), line 120 (`call_ai`, correct — both providers failed). Line 14 is inside a docstring. No sys.exit inside `call_claude` or `call_openai`.
- `generate_exercises.py` is unchanged; `call_ai()` interface is backward-compatible.

---

### Human Verification Required

None. All observable behaviors were verifiable programmatically:
- Fallback retry: covered by unit tests with mocks.
- stderr logging content: covered by `capsys` in `test_call_ai_fallback_logs_to_stderr`.
- Exit code on dual failure: covered by `test_call_ai_fallback_both_fail_exits`.
- Full suite integrity: confirmed by `pytest` 108/108.

---

### Commits Verified

| Hash    | Description                                             | Files Modified              |
|---------|---------------------------------------------------------|-----------------------------|
| acb69b5 | test(05-01): add failing test stubs for provider fallback (RED) | tests/test_ai_provider.py |
| 23ba05f | feat(05-01): implement provider fallback in ai_provider.py (GREEN) | scripts/ai_provider.py |

Both commits exist in the repository and modified exactly the files declared in the plan's `files_modified` list.

---

_Verified: 2026-03-23T12:00:00+08:00_
_Verifier: Claude (gsd-verifier)_
