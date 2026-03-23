---
phase: 5
slug: fallback-logic
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-23
---

# Phase 5 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (existing) |
| **Config file** | `pytest.ini` (pythonpath = .) |
| **Quick run command** | `pytest tests/test_ai_provider.py -x` |
| **Full suite command** | `pytest` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/test_ai_provider.py -x`
- **After every plan wave:** Run `pytest`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 5-01-01 | 01 | 0 | FALL-01, FALL-02, FALL-03, TEST-02 | unit | `pytest tests/test_ai_provider.py -x` | Wave 0 (new stubs) | ⬜ pending |
| 5-01-02 | 01 | 1 | FALL-01 | unit | `pytest tests/test_ai_provider.py::test_call_ai_fallback_primary_fails_backup_succeeds -x` | ✅ after Wave 0 | ⬜ pending |
| 5-01-03 | 01 | 1 | FALL-01 | unit | `pytest tests/test_ai_provider.py::test_call_ai_fallback_openai_primary_fails -x` | ✅ after Wave 0 | ⬜ pending |
| 5-01-04 | 01 | 1 | FALL-02 | unit | `pytest tests/test_ai_provider.py::test_call_ai_fallback_both_fail_exits -x` | ✅ after Wave 0 | ⬜ pending |
| 5-01-05 | 01 | 1 | FALL-03 | unit | `pytest tests/test_ai_provider.py::test_call_ai_fallback_logs_to_stderr -x` | ✅ after Wave 0 | ⬜ pending |
| 5-01-06 | 01 | 1 | FALL-01, FALL-02 | unit | `pytest tests/test_ai_provider.py -x` | ✅ existing | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_ai_provider.py` — add stub test functions for FALL-01 (×2), FALL-02, FALL-03; update existing `test_call_claude_exits_on_api_error` and `test_call_openai_exits_on_error` to assert `ProviderError` instead of `SystemExit`

*No new files needed — extends existing `tests/test_ai_provider.py`*

---

## Manual-Only Verifications

All phase behaviors have automated verification.

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
