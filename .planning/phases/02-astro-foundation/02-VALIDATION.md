---
phase: 02
slug: astro-foundation
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-24
---

# Phase 02 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | vitest (unit) + Playwright (E2E) / build smoke tests |
| **Config file** | `website/vitest.config.ts` — Wave 0 installs |
| **Quick run command** | `cd website && npm run build 2>&1 | tail -5` |
| **Full suite command** | `cd website && npm run build && npx astro check` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Run `cd website && npm run build 2>&1 | tail -5`
- **After every plan wave:** Run `cd website && npm run build && npx astro check`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 60 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 02-01-01 | 01 | 1 | SITE-04 | build | `cd website && npm run build` | ❌ W0 | ⬜ pending |
| 02-01-02 | 01 | 1 | SITE-01 | build | `cd website && npm run build` | ❌ W0 | ⬜ pending |
| 02-02-01 | 02 | 2 | SITE-02 | CI smoke | `gh workflow run deploy.yml` | ❌ W0 | ⬜ pending |
| 02-02-02 | 02 | 2 | SITE-03 | build | `cd website && npm run build 2>&1 | grep -v ERROR` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `website/package.json` — Astro + Tailwind 4 dependencies defined
- [ ] `website/astro.config.mjs` — base config with GitHub Pages path
- [ ] `website/src/content.config.ts` — content collection schema
- [ ] `website/src/pages/index.astro` — lesson list page stub

*Existing Python infrastructure is unaffected — all Wave 0 is in `website/`.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Live site renders in browser | SITE-01 | Requires deployed GitHub Pages URL | Open `https://<username>.github.io/study-all/` after deploy |
| Auto-deploy triggers on push | SITE-02 | Requires actual git push to remote | Push a new `content/YYYY-MM-DD.md`, verify Actions run passes |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 60s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

---

## Validation Audit 2026-03-24

| Metric | Count |
|--------|-------|
| Gaps found | 3 |
| Resolved | 0 |
| Escalated (manual-only) | 0 |
| Skipped (Wave 0 unmet) | 3 |

**Audit notes:** All MISSING items (`SITE-04`, `SITE-01`, `SITE-03`) have automated build commands defined. They are unrunnable because `website/` has not been scaffolded yet — Wave 0 is a precondition. Validation strategy is structurally sound. Re-run `/gsd:validate-phase 02` after Phase 02 execution to confirm green.
