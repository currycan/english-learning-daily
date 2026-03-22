---
phase: 01-foundation
plan: 02
subsystem: infra
tags: [github-actions, pytest, subprocess, idempotency, ci-cd]

# Dependency graph
requires:
  - phase: 01-foundation-01-01
    provides: scripts/content_utils.py with get_beijing_date, content_path, CONTENT_DIR
provides:
  - scripts/commit_content.py — idempotency guard, writes placeholder, commits with correct message
  - tests/test_commit_content.py — 4 pytest tests covering all behaviors
  - .github/workflows/daily-content.yml — cron-triggered CI workflow with write permissions and git identity
affects: [02-content-fetcher, 03-ai-enrichment]

# Tech tracking
tech-stack:
  added: []
  patterns: [subprocess-with-calledprocesserror-exit-1, idempotency-via-path-exists, tdd-red-green]

key-files:
  created:
    - scripts/commit_content.py
    - tests/test_commit_content.py
    - .github/workflows/daily-content.yml
  modified: []

key-decisions:
  - "Idempotency guard uses path.exists() check and sys.exit(0) — consistent with plan spec"
  - "git_commit_and_push takes (path, today) args matching test signatures exactly"
  - "Workflow permissions: contents: write at job level (not workflow level) to follow least-privilege"
  - "Cron 0 22 * * * (22:00 UTC = 06:00 BJT) distinct from morning.yml's 0 23 * * *"

patterns-established:
  - "Pattern: Idempotency guard — check path.exists() first, sys.exit(0) if already done"
  - "Pattern: Git failure via subprocess.CalledProcessError — always sys.exit(1) with ERROR to stderr"
  - "Pattern: GitHub Actions workflow with contents: write at job level for git push via GITHUB_TOKEN"

requirements-completed: [CI-01, CI-02]

# Metrics
duration: 2min
completed: 2026-03-23
---

# Phase 1 Plan 02: CI Scaffold — commit_content.py and daily-content.yml Summary

**Idempotency-guarded placeholder commit script (exits 0 on re-run) plus GitHub Actions workflow with contents: write permissions and git identity config**

## Performance

- **Duration:** 2 min
- **Started:** 2026-03-22T16:05:56Z
- **Completed:** 2026-03-22T16:07:57Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments

- Implemented scripts/commit_content.py with idempotency guard (exits 0 when file exists), placeholder write, and git commit using "content: add YYYY-MM-DD" format
- Wrote 4 pytest tests via TDD (RED then GREEN): skips when file exists, writes placeholder when absent, git failure exits 1, commit message format verified
- Created .github/workflows/daily-content.yml with cron 0 22 * * *, workflow_dispatch, contents: write, git identity configuration, and python -m scripts.commit_content

## Task Commits

Each task was committed atomically:

1. **Task 1: Write tests then implement commit_content.py** - `38da494` (feat)
2. **Task 2: Create daily-content.yml CI workflow** - `ce8e6dc` (feat)

**Plan metadata:** (docs commit — see below)

_Note: Task 1 used TDD — tests written first (RED), then implementation (GREEN)_

## Files Created/Modified

- `scripts/commit_content.py` — Idempotency guard, placeholder write, git commit/push with exit-1 on failure
- `tests/test_commit_content.py` — 4 tests: skips existing, writes absent, git failure exits 1, commit message format
- `.github/workflows/daily-content.yml` — Daily cron + workflow_dispatch, contents: write, git identity, python -m scripts.commit_content

## Decisions Made

- `git_commit_and_push` takes `(path: Path, today: date)` args — allows tests to verify commit message format with injected date without monkeypatching date.today()
- Workflow uses `permissions: contents: write` at job level (not workflow level) — least-privilege approach
- No BARK_TOKEN env var in workflow — this workflow never calls the Bark API

## Deviations from Plan

None — plan executed exactly as written.

## Issues Encountered

PyYAML not installed in venv (not in requirements.txt), so plan's yaml-based verification command could not run. Verified all required fields using grep instead — all 7 elements confirmed present. This is expected since requirements.txt only contains requests and pytest.

## User Setup Required

None — no external service configuration required. The workflow uses GITHUB_TOKEN (automatically provided by GitHub Actions) for git push.

## Next Phase Readiness

- Phase 1 CI scaffold complete: content_utils.py + commit_content.py + daily-content.yml all in place
- Workflow can be triggered via workflow_dispatch on GitHub to verify end-to-end behavior
- Phase 2 (content fetcher) can now write to content/YYYY-MM-DD.md and the CI will commit it

---
*Phase: 01-foundation*
*Completed: 2026-03-23*
