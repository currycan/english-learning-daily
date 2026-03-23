---
phase: 4
slug: provider-abstraction-openai-integration
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-23
---

# Phase 4 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.3.5 |
| **Config file** | none — pytest discovers `tests/` automatically |
| **Quick run command** | `pytest tests/test_ai_provider.py -x` |
| **Full suite command** | `pytest` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/test_ai_provider.py -x`
- **After every plan wave:** Run `pytest`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** ~5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 4-01-01 | 01 | 0 | PRVD-01 | unit | `pytest tests/test_ai_provider.py::test_call_ai_dispatches_anthropic -x` | ❌ W0 | ⬜ pending |
| 4-01-02 | 01 | 0 | PRVD-01 | unit | `pytest tests/test_ai_provider.py::test_call_ai_dispatches_openai -x` | ❌ W0 | ⬜ pending |
| 4-01-03 | 01 | 0 | PRVD-02 | unit | `pytest tests/test_ai_provider.py::test_resolve_provider_env_var_priority -x` | ❌ W0 | ⬜ pending |
| 4-01-04 | 01 | 0 | PRVD-02 | unit | `pytest tests/test_ai_provider.py::test_resolve_provider_unknown_exits -x` | ❌ W0 | ⬜ pending |
| 4-01-05 | 01 | 0 | PRVD-03 | unit | `pytest tests/test_ai_provider.py::test_resolve_provider_config_default -x` | ❌ W0 | ⬜ pending |
| 4-01-06 | 01 | 0 | OAPI-01 | unit | `pytest tests/test_ai_provider.py::test_call_openai_returns_content -x` | ❌ W0 | ⬜ pending |
| 4-01-07 | 01 | 0 | OAPI-01 | unit | `pytest tests/test_ai_provider.py::test_call_openai_exits_on_error -x` | ❌ W0 | ⬜ pending |
| 4-01-08 | 01 | 0 | OAPI-02 | unit | `pytest tests/test_ai_provider.py::test_call_openai_uses_configured_model -x` | ❌ W0 | ⬜ pending |
| 4-01-09 | 01 | 0 | TEST-01 | unit | `pytest tests/test_ai_provider.py -x` | ❌ W0 | ⬜ pending |
| 4-02-01 | 02 | 1 | OAPI-03 | manual | grep audit of source + config.json | N/A | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_ai_provider.py` — stubs for PRVD-01, PRVD-02, PRVD-03, OAPI-01, OAPI-02, TEST-01
- [ ] `scripts/ai_provider.py` — module under test must exist before tests can be written

*Existing test infrastructure is complete; only the new module and its test file are missing.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| `OPENAI_API_KEY` never in source or config files | OAPI-03 | Static audit — no runtime path to verify absence | `grep -r "OPENAI_API_KEY" scripts/ plan/config.json` — should return zero results (no hardcoded values) |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
