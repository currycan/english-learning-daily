---
phase: 6
slug: ai-provider-documentation
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-23
---

# Phase 6 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x |
| **Config file** | pytest.ini / pyproject.toml |
| **Quick run command** | `pytest tests/ -q` |
| **Full suite command** | `pytest tests/ -v` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/ -q`
- **After every plan wave:** Run `pytest tests/ -v`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 6-01-01 | 01 | 1 | DOCS-01, DOCS-02 | manual | `test -f docs/ai-providers.md` | ❌ W0 | ⬜ pending |
| 6-01-02 | 01 | 1 | DOCS-03 | manual | `grep -q 'OPENAI_API_KEY' docs/ai-providers.md` | ❌ W0 | ⬜ pending |
| 6-01-03 | 01 | 1 | DOCS-04 | manual | `grep -q 'AI_PROVIDER' docs/ai-providers.md` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `docs/ai-providers.md` — create the file (deliverable itself)

*Existing test infrastructure covers all phase requirements — this is a documentation-only phase.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Step-by-step instructions for OpenAI API key | DOCS-01 | Content quality check — requires human review | Read `docs/ai-providers.md`, verify instructions are clear and accurate for obtaining OpenAI API key from platform.openai.com |
| Step-by-step instructions for Anthropic API key | DOCS-02 | Content quality check — requires human review | Read `docs/ai-providers.md`, verify instructions are clear and accurate for obtaining Anthropic API key from console.anthropic.com |
| GitHub Actions Secrets setup instructions | DOCS-03 | Content quality check — requires human review | Read `docs/ai-providers.md`, verify instructions explain adding `OPENAI_API_KEY` and `ANTHROPIC_API_KEY` as GitHub Repository Secrets |
| Priority rule documented correctly | DOCS-04 | Correctness check — must match code | Verify doc states `AI_PROVIDER` env var overrides `ai_provider` in `plan/config.json`; cross-check with `scripts/ai_provider.py` lines 7-14 |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
