---
phase: 1
slug: claude-openai-api-key-gemini-api
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-24
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest |
| **Config file** | pytest.ini or pyproject.toml (if exists) |
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
| 1-01-01 | 01 | 1 | Gemini SDK | unit | `pytest tests/test_ai_provider.py -v` | ✅ | ⬜ pending |
| 1-01-02 | 01 | 1 | Config fields | unit | `pytest tests/test_ai_provider.py -v` | ✅ | ⬜ pending |
| 1-01-03 | 01 | 1 | CI workflow | manual | inspect .github/workflows/daily-content.yml | ✅ | ⬜ pending |
| 1-01-04 | 01 | 2 | Test rewrite | unit | `pytest` | ✅ | ⬜ pending |
| 1-01-05 | 01 | 2 | Docs update | manual | inspect docs/ai-providers.md | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- Existing infrastructure covers all phase requirements. (`tests/test_ai_provider.py` and `tests/test_ai_provider_docs.py` exist and will be rewritten, not added.)

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| GitHub Actions secret GEMINI_API_KEY | CI integration | Cannot be set via code | Verify in repo Settings → Secrets → GEMINI_API_KEY exists |
| CI workflow runs successfully | End-to-end | Requires push to trigger | Push commit and verify Actions run passes |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
