---
phase: 03-ai-pipeline
plan: 03
subsystem: infra
tags: [github-actions, anthropic, python, pipes, ci, content-pipeline]

# Dependency graph
requires:
  - phase: 03-ai-pipeline-01
    provides: tests/test_commit_content.py with test_reads_stdin_and_writes_file (RED)
  - phase: 03-ai-pipeline-02
    provides: scripts/generate_exercises.py (middle pipe stage)
provides:
  - commit_content.py main() reads real Markdown from stdin and writes it to content/YYYY-MM-DD.md
  - daily-content.yml three-stage pipeline with set -eo pipefail and ANTHROPIC_API_KEY injection
affects: [workflow-runs, ci, content-output]

# Tech tracking
tech-stack:
  added: []
  patterns: [stdin-pipe-chaining, pipefail-error-propagation, empty-content-guard]

key-files:
  created: []
  modified:
    - scripts/commit_content.py
    - tests/test_commit_content.py
    - .github/workflows/daily-content.yml

key-decisions:
  - "main() uses sys.stdin.read() + empty-content guard (sys.exit(1)) instead of placeholder write_text"
  - "set -eo pipefail ensures intermediate pipe failures propagate as CI failures (not silently succeed)"
  - "ANTHROPIC_API_KEY injected via step env block — GitHub Secrets require explicit mapping"

patterns-established:
  - "Stdin-pipe pattern: each script reads stdin, writes stdout; commit_content is the final consumer"
  - "Idempotency guard uses stderr for skip message (not stdout) to avoid polluting pipe output"

requirements-completed: [OUT-02, OUT-03]

# Metrics
duration: 8min
completed: 2026-03-23
---

# Phase 3 Plan 03: Wire Pipeline Summary

**commit_content.py main() now reads real Markdown from stdin via sys.stdin.read() and daily-content.yml runs the full feed_article | generate_exercises | commit_content three-stage pipe with pipefail and API key injection**

## Performance

- **Duration:** 8 min
- **Started:** 2026-03-23T02:00:00Z
- **Completed:** 2026-03-23T02:08:00Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments
- Replaced placeholder write_text in commit_content.py main() with sys.stdin.read() + empty-content guard
- Updated test_writes_placeholder_when_file_absent to patch sys.stdin (maintains test correctness)
- All 90 tests pass including the new test_reads_stdin_and_writes_file (GREEN state achieved)
- Updated daily-content.yml last step to run the full three-stage pipeline with set -eo pipefail and ANTHROPIC_API_KEY env injection

## Task Commits

Each task was committed atomically:

1. **Task 1: Replace commit_content.py main() to read stdin Markdown** - `8158ff1` (feat)
2. **Task 2: Update daily-content.yml to run the three-stage pipeline** - `8e4db04` (feat)

**Plan metadata:** (docs commit follows)

## Files Created/Modified
- `scripts/commit_content.py` - main() now reads stdin Markdown; empty-content guard added; git_commit_and_push unchanged
- `tests/test_commit_content.py` - test_writes_placeholder_when_file_absent updated to patch sys.stdin
- `.github/workflows/daily-content.yml` - Last step replaced with three-stage pipeline + set -eo pipefail + ANTHROPIC_API_KEY

## Decisions Made
- Used sys.stdin.read() in main() so the script is the final consumer in a shell pipe
- Empty-content guard prints to stderr to avoid polluting pipe; exits 1 so CI fails fast
- Skip message now writes to stderr (was stdout) to avoid any interference with pipe signaling
- set -eo pipefail in workflow ensures a failure in feed_article or generate_exercises is not silently swallowed

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None - all tests passed on first run after implementing changes.

## Next Phase Readiness
- Phase 3 AI pipeline is now complete end-to-end
- Running the workflow will: fetch RSS article, generate exercises via Claude API, commit Markdown to content/YYYY-MM-DD.md
- ANTHROPIC_API_KEY must be set as a GitHub repository secret before first workflow run

---
*Phase: 03-ai-pipeline*
*Completed: 2026-03-23*
