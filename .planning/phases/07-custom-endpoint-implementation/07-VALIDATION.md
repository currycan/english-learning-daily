---
phase: 7
slug: custom-endpoint-implementation
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-23
---

# Phase 7 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest |
| **Config file** | `pytest.ini` / `pyproject.toml` (existing) |
| **Quick run command** | `pytest tests/test_ai_provider.py -v` |
| **Full suite command** | `pytest` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/test_ai_provider.py -v`
- **After every plan wave:** Run `pytest`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 7-01-01 | 01 | 1 | TPROV-01, TPROV-02 | unit | `pytest tests/test_ai_provider.py::test_custom_endpoint_env_vars -v` | ✅ | ⬜ pending |
| 7-01-02 | 01 | 1 | TPROV-03 | unit | `pytest tests/test_ai_provider.py::test_backward_compat_no_custom_params -v` | ✅ | ⬜ pending |
| 7-01-03 | 01 | 1 | CONF-01, CONF-02 | unit | `pytest tests/test_ai_provider.py::test_config_fallback_path -v` | ✅ | ⬜ pending |
| 7-01-04 | 01 | 2 | TPROV-04 | unit | `pytest tests/test_ai_provider.py -v` | ✅ | ⬜ pending |
| 7-02-01 | 02 | 1 | TEST-01, TEST-02 | unit | `pytest tests/test_ai_provider.py -v` | ✅ | ⬜ pending |
| 7-02-02 | 02 | 1 | CONF-03, CONF-04 | unit | `pytest tests/test_ai_provider.py -v` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements.
- `tests/test_ai_provider.py` already exists with `patch("scripts.ai_provider.anthropic.Anthropic")` pattern
- pytest already installed and configured
- New test functions will be added in-place (no new test files needed)

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
