---
phase: 07-custom-endpoint-implementation
plan: "03"
subsystem: infra
tags: [github-actions, ci, secrets, env-vars, anthropic]

# Dependency graph
requires:
  - phase: 07-custom-endpoint-implementation-01
    provides: call_claude() reads ANTHROPIC_BASE_URL and ANTHROPIC_AUTH_TOKEN from os.environ
provides:
  - CI step-level env injects ANTHROPIC_BASE_URL and ANTHROPIC_AUTH_TOKEN from GitHub secrets
affects: [08-docs]

# Tech tracking
tech-stack:
  added: []
  patterns: [step-level env for optional secrets — empty string from missing secrets treated as absent by call_claude()]

key-files:
  created: []
  modified:
    - .github/workflows/daily-content.yml

key-decisions:
  - "New env vars placed in step-level env block only, not top-level — secrets are scoped to the generate step"
  - "No conditional YAML logic — GitHub returns empty string for missing secrets, which call_claude() treats as absent (no behavioral change)"
  - "Alphabetical ordering within Anthropic group: ANTHROPIC_API_KEY, ANTHROPIC_AUTH_TOKEN, ANTHROPIC_BASE_URL — then OPENAI_API_KEY"

patterns-established:
  - "Optional secrets injected unconditionally at step-level; absence is handled at runtime by the consuming code"

requirements-completed: [CONF-04, TPROV-04]

# Metrics
duration: 1min
completed: 2026-03-23
---

# Phase 7 Plan 03: CI Workflow Secrets Injection Summary

**Two optional Anthropic secrets (ANTHROPIC_BASE_URL, ANTHROPIC_AUTH_TOKEN) injected into the GitHub Actions step-level env block for call_claude() custom endpoint support**

## Performance

- **Duration:** ~1 min
- **Started:** 2026-03-23T06:18:25Z
- **Completed:** 2026-03-23T06:19:17Z
- **Tasks:** 1
- **Files modified:** 1

## Accomplishments
- Added `ANTHROPIC_BASE_URL: ${{ secrets.ANTHROPIC_BASE_URL }}` to the "Generate and commit daily content" step env block
- Added `ANTHROPIC_AUTH_TOKEN: ${{ secrets.ANTHROPIC_AUTH_TOKEN }}` to the same step env block
- Preserved existing `ANTHROPIC_API_KEY` and `OPENAI_API_KEY` lines unchanged
- Top-level `env:` block (FORCE_JAVASCRIPT_ACTIONS_TO_NODE24 only) not touched

## Task Commits

Each task was committed atomically:

1. **Task 1: Add ANTHROPIC_BASE_URL and ANTHROPIC_AUTH_TOKEN to CI step env block** - `e4f3ad5` (feat)

**Plan metadata:** (docs commit — see below)

## Files Created/Modified
- `.github/workflows/daily-content.yml` - Added two step-level env vars for custom endpoint secrets

## Decisions Made
- Placed new env vars at step level (not top level) so secrets are scoped to only the generate step
- No conditional YAML — GitHub returns "" for missing secrets; call_claude() handles the empty-string-as-absent logic at runtime
- Alphabetical ordering within Anthropic group maintained

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

Two new GitHub repository secrets must be added to enable custom endpoint routing:

| Secret | Description |
|--------|-------------|
| `ANTHROPIC_BASE_URL` | Custom base URL for Anthropic API (e.g. proxy endpoint) |
| `ANTHROPIC_AUTH_TOKEN` | Auth token for the custom endpoint |

If these secrets are not set, GitHub returns empty string, and call_claude() continues using the standard Anthropic API via `ANTHROPIC_API_KEY` — no behavioral change.

## Next Phase Readiness
- CI is now fully wired: ANTHROPIC_BASE_URL and ANTHROPIC_AUTH_TOKEN will be available as env vars when call_claude() runs during CI
- Phase 7 implementation complete (plans 01-03 done); Phase 8 docs can proceed

---
*Phase: 07-custom-endpoint-implementation*
*Completed: 2026-03-23*
