---
phase: 2
slug: rss-fetch
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-23
---

# Phase 2 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x |
| **Config file** | pytest.ini or pyproject.toml (existing) |
| **Quick run command** | `pytest tests/test_fetch_article.py -v` |
| **Full suite command** | `pytest -v` |
| **Estimated runtime** | ~10 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/test_fetch_article.py -v`
- **After every plan wave:** Run `pytest -v`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 2-01-01 | 01 | 0 | FTCH-01 | unit | `pytest tests/test_fetch_article.py::test_article_envelope_schema -v` | ❌ W0 | ⬜ pending |
| 2-01-02 | 01 | 1 | FTCH-01 | unit | `pytest tests/test_fetch_article.py::test_voa_fetch_returns_envelope -v` | ❌ W0 | ⬜ pending |
| 2-01-03 | 01 | 1 | FTCH-02 | unit | `pytest tests/test_fetch_article.py::test_fallback_when_voa_fails -v` | ❌ W0 | ⬜ pending |
| 2-01-04 | 01 | 1 | FTCH-03 | unit | `pytest tests/test_fetch_article.py::test_exits_nonzero_when_both_fail -v` | ❌ W0 | ⬜ pending |
| 2-01-05 | 01 | 1 | FTCH-01 | unit | `pytest tests/test_fetch_article.py::test_body_min_200_chars -v` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_fetch_article.py` — stubs for FTCH-01, FTCH-02, FTCH-03
- [ ] `tests/conftest.py` — shared fixtures (mock feedparser responses)
- [ ] Validate live feed URLs in `plan/config.json` before implementation

*Existing pytest infrastructure detected — only test stubs and fixture setup needed.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Live VOA feed returns real English prose | FTCH-01 | Requires live network access; feed URLs may change | Run `python -m scripts.fetch_article` and verify output contains natural English article text |
| HTML stripping produces clean prose | FTCH-01 | Content varies; hard to assert exact text | Inspect `body` field manually for absence of HTML tags and presence of readable sentences |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
