---
phase: 8
slug: third-party-provider-documentation
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-23
---

# Phase 8 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x |
| **Config file** | `pytest.ini` / `pyproject.toml` |
| **Quick run command** | `pytest tests/test_ai_provider_docs.py -v` |
| **Full suite command** | `pytest` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/test_ai_provider_docs.py -v`
- **After every plan wave:** Run `pytest`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 8-01-01 | 01 | 0 | DOCS-01, DOCS-02, DOCS-03 | unit | `pytest tests/test_ai_provider_docs.py -v` | ❌ W0 | ⬜ pending |
| 8-01-02 | 01 | 1 | DOCS-01 | unit | `pytest tests/test_ai_provider_docs.py::test_section5_exists -v` | ✅ W0 | ⬜ pending |
| 8-01-03 | 01 | 1 | DOCS-02 | unit | `pytest tests/test_ai_provider_docs.py::test_config_example -v` | ✅ W0 | ⬜ pending |
| 8-01-04 | 01 | 1 | DOCS-03 | unit | `pytest tests/test_ai_provider_docs.py::test_github_secrets_section -v` | ✅ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_ai_provider_docs.py` — add stub test functions for DOCS-01, DOCS-02, DOCS-03 (file exists but stubs are missing)

*Existing `tests/test_ai_provider_docs.py` exists but lacks test functions for v1.2 DOCS requirements. Wave 0 must add failing stubs before any documentation is written.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Bilingual prose reads naturally in English and Chinese | DOCS-01 | Language quality cannot be automated | Read Section 5 prose aloud; verify Chinese paragraphs accurately translate the English |
| GitHub Secrets steps match current GitHub UI | DOCS-03 | UI may differ from automated checks | Follow steps in Section 5 on a test repo and confirm each UI element exists |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
