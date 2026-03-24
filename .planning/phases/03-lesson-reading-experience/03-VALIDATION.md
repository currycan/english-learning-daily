---
phase: 03
slug: lesson-reading-experience
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-24
---

# Phase 03 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (Python) for Python scripts; Vitest (JS) for parser utilities — Wave 0 installs Vitest |
| **Config file** | `pytest.ini` (Python) / `website/vitest.config.ts` (Wave 0 installs) |
| **Quick run command** | `pytest tests/ -x -q && cd website && npx vitest run --reporter=verbose` |
| **Full suite command** | `pytest tests/ -v && cd website && npx vitest run` |
| **Estimated runtime** | ~10 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/ -x -q` (Python) + manual browser check of affected page
- **After every plan wave:** Run full suite (pytest + vitest) + manual mobile UAT
- **Before `/gsd:verify-work`:** Full suite must be green + manual UAT checklist complete
- **Max feedback latency:** ~10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 03-01-W0 | 01 | 0 | LESS-01,02,03 | unit | `cd website && npx vitest run src/lib/lesson-parser.test.ts` | ❌ W0 | ⬜ pending |
| 03-01-01 | 01 | 1 | LESS-01 | unit | `cd website && npx vitest run --reporter=verbose` | ✅ W0 | ⬜ pending |
| 03-01-02 | 01 | 1 | LESS-02 | unit | `cd website && npx vitest run --reporter=verbose` | ✅ W0 | ⬜ pending |
| 03-01-03 | 01 | 1 | LESS-03 | unit | `cd website && npx vitest run --reporter=verbose` | ✅ W0 | ⬜ pending |
| 03-01-04 | 01 | 1 | LESS-04 | manual | Build succeeds + article visible without interaction | N/A | ⬜ pending |
| 03-02-01 | 02 | 2 | LESS-05 | manual | Tap vocabulary header → section expands/collapses | N/A | ⬜ pending |
| 03-02-02 | 02 | 2 | LESS-06 | manual | Tap expressions header → section expands/collapses | N/A | ⬜ pending |
| 03-02-03 | 02 | 2 | LESS-07 | manual | Tap comprehension header → section expands/collapses | N/A | ⬜ pending |
| 03-02-04 | 02 | 2 | LESS-08 | manual | Tap "查看答案" → EN + ZH answer appears | N/A | ⬜ pending |
| 03-02-05 | 02 | 2 | LESS-09 | manual | DevTools mobile view — body text ≥16px, tap targets ≥44px | N/A | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `website/vitest.config.ts` — Vitest config for testing parser utilities
- [ ] `website/src/lib/lesson-parser.ts` — extracted pure parser functions (`parseSections`, `extractSourceUrl`, `extractPreview`, `parseComprehension`, `getTodayShanghai`)
- [ ] `website/src/lib/lesson-parser.test.ts` — unit tests for all parser functions (covers LESS-01, LESS-02, LESS-03 logic)
- [ ] Install Vitest: `cd website && npm install -D vitest`

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Article text always visible without interaction | LESS-04 | Static rendering — no runtime assertion needed | Open lesson page; verify article section is visible on load, no button required |
| Vocabulary section collapse/expand with animation | LESS-05 | Runtime JS behavior | Open lesson page; tap 📚 header; verify smooth expand/collapse; chevron rotates |
| Expressions section collapse/expand | LESS-06 | Runtime JS behavior | Open lesson page; tap 🔗 header; verify independent of other sections |
| Comprehension section collapse/expand | LESS-07 | Runtime JS behavior | Open lesson page; tap ❓ header; verify section expands showing all questions |
| Tap-to-reveal Q&A | LESS-08 | Runtime JS behavior | Expand comprehension; tap "查看答案" on each question; verify EN + ZH both appear |
| Mobile sizing | LESS-09 | Visual/layout check | Chrome DevTools → iPhone SE; verify body text ≥16px, all tap targets ≥44px height |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
