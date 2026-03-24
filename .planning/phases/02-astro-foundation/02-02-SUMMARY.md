---
phase: 02-astro-foundation
plan: 02
subsystem: infra
tags: [github-actions, github-pages, astro, ci-cd, deploy]

# Dependency graph
requires:
  - phase: 02-01
    provides: Astro 6 project in website/ with package-lock.json committed for npm ci
provides:
  - build-and-deploy job in daily-content.yml that builds Astro site and deploys to GitHub Pages
  - Live site at https://currycan.github.io/study-all/ serving lesson list and stub lesson pages
  - End-to-end CI/CD pipeline: content commit -> generate-content -> build-and-deploy -> Pages
affects: [03-reading-ux, 04-archive-calendar, 05-theme-polish]

# Tech tracking
tech-stack:
  added:
    - actions/setup-node@v4 (Node 22 in CI)
    - actions/upload-pages-artifact@v3
    - actions/deploy-pages@v4
  patterns:
    - build-and-deploy job appended to existing workflow (not a separate workflow_run file)
    - Each job gets a fresh runner — actions/checkout@v4 required in every job
    - npm ci (not npm install) for reproducible CI builds
    - working-directory: ./website isolates Node steps from Python environment

key-files:
  created: []
  modified:
    - .github/workflows/daily-content.yml

key-decisions:
  - "build-and-deploy job appended to daily-content.yml with needs: generate-content (always rebuilds on content commit)"
  - "Each job on GitHub Actions runs on a fresh runner — checkout@v4 required even though generate-content already checked out"
  - "npm ci used (not npm install) to guarantee reproducible builds from committed package-lock.json"
  - "GitHub Pages source set to GitHub Actions (not Deploy from branch) — required for actions/deploy-pages to work"

patterns-established:
  - "Pattern: CI jobs that need repo files must include actions/checkout@v4 — runners are ephemeral"
  - "Pattern: working-directory: ./website on all Node steps keeps CI environment isolated"

requirements-completed: [SITE-01, SITE-02]

# Metrics
duration: continuation (Task 1 auto, Task 2 human-verify approved)
completed: 2026-03-24
---

# Phase 02 Plan 02: Astro Foundation Summary

**build-and-deploy job added to daily-content.yml, deploying Astro site to GitHub Pages via actions/deploy-pages@v4; live at https://currycan.github.io/study-all/**

## Performance

- **Duration:** continuation plan (Task 1 automated, Task 2 human-verify checkpoint)
- **Started:** 2026-03-24
- **Completed:** 2026-03-24
- **Tasks:** 2
- **Files modified:** 1

## Accomplishments

- Added build-and-deploy job to .github/workflows/daily-content.yml with needs: generate-content
- Job checks out repo, installs Node 22, runs npm ci + npm run build inside website/, uploads artifact, deploys to GitHub Pages
- Live site at https://currycan.github.io/study-all/ confirmed accessible by human verifier
- Both generate-content and build-and-deploy jobs complete green; CI/CD pipeline proven end-to-end

## Task Commits

Each task was committed atomically:

1. **Task 1: Add build-and-deploy job to daily-content.yml** - `35051f0` (feat)
2. **Task 2: Verify GitHub Pages deployment is live** - human-verify checkpoint, approved by user

**Plan metadata:** _(docs commit follows)_

## Files Created/Modified

- `.github/workflows/daily-content.yml` - Appended build-and-deploy job with permissions, environment, checkout, Node 22, npm ci, npm run build in website/, upload-pages-artifact, deploy-pages steps

## Decisions Made

- `build-and-deploy` job uses `needs: generate-content` — always triggers after content generation on every push, ensuring site is always in sync with latest content.
- Fresh checkout required in each CI job — GitHub Actions runners are ephemeral, prior job's checkout is not available.
- `npm ci` chosen over `npm install` for reproducible builds; requires the committed `package-lock.json` from Plan 01.
- GitHub Pages source manually set to "GitHub Actions" (one-time prerequisite documented in Plan 01 SUMMARY).

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

GitHub Pages source was set to "GitHub Actions" (documented in Plan 01 as one-time prerequisite). No additional setup required for future deployments — every content commit now triggers an automatic rebuild and deploy.

## Next Phase Readiness

- Full CI/CD pipeline is live: content/*.md commit -> generate-content -> build-and-deploy -> GitHub Pages
- Phase 03 (reading UX) can now build on the live site — stub lesson pages at /lesson/YYYY-MM-DD are accessible
- Phase 04 (archive calendar) and Phase 05 (theme & polish) both have a working deployment target

---
*Phase: 02-astro-foundation*
*Completed: 2026-03-24*

## Self-Check: PASSED

- Task 1 commit 35051f0 verified in git log
- .github/workflows/daily-content.yml contains build-and-deploy job (committed in 35051f0)
- Task 2 human-verify checkpoint approved by user — live site confirmed at https://currycan.github.io/study-all/
