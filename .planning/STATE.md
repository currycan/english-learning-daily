---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
status: planning
stopped_at: Completed 03-ai-pipeline-02-PLAN.md
last_updated: "2026-03-23T01:42:49.563Z"
last_activity: 2026-03-22 — Roadmap created
progress:
  total_phases: 3
  completed_phases: 2
  total_plans: 7
  completed_plans: 6
  percent: 0
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-03-22)

**Core value:** Every day a ready-to-read English lesson lands in git — real content with targeted vocabulary, chunking expressions, and exercises to deepen understanding.
**Current focus:** Phase 1 — Foundation

## Current Position

Phase: 1 of 3 (Foundation)
Plan: 0 of TBD in current phase
Status: Ready to plan
Last activity: 2026-03-22 — Roadmap created

Progress: [░░░░░░░░░░] 0%

## Performance Metrics

**Velocity:**
- Total plans completed: 0
- Average duration: -
- Total execution time: 0 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| - | - | - | - |

**Recent Trend:**
- Last 5 plans: none yet
- Trend: -

*Updated after each plan completion*
| Phase 01-foundation P01 | 2 | 1 tasks | 2 files |
| Phase 01-foundation P02 | 3min | 2 tasks | 3 files |
| Phase 02-rss-fetch P01 | 8min | 2 tasks | 3 files |
| Phase 02-rss-fetch P02 | 3min | 1 tasks | 1 files |
| Phase 03-ai-pipeline P01 | 106 | 3 tasks | 3 files |
| Phase 03-ai-pipeline P02 | 106 | 1 tasks | 1 files |

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- [Init]: Use feedparser (not xml.etree) for RSS — handles malformed XML and CDATA blocks
- [Init]: Use claude-3-5-haiku-20241022 (pinned) — cost-efficient at ~1,400 tokens/day
- [Init]: VOA Special English as primary RSS source — already B1-B2 calibrated, no extra filtering needed
- [Init]: One Claude API call per day — single structured JSON prompt covering vocabulary + chunks + questions
- [Phase 01-foundation]: Use datetime.now(tz=BEIJING_TZ).date() not date.today() to correctly derive Beijing date on UTC runners
- [Phase 01-foundation]: Patch datetime in module namespace for testability: monkeypatch.setattr(cu, 'datetime', FakeDatetime)
- [Phase 01-foundation]: Idempotency guard uses path.exists() check and sys.exit(0); git_commit_and_push takes (path, today) args for testability; Workflow permissions: contents: write at job level
- [Phase 02-rss-fetch]: newsinlevels.com/feed confirmed as ONLY verified primary RSS URL returning 800+ char body via content:encoded
- [Phase 02-rss-fetch]: BBC Learning English fallback kept per locked user decision; retry logic handles gracefully if it also returns short content
- [Phase 02-rss-fetch]: Used HTMLParser subclass (_TextExtractor) instead of regex for HTML cleaning — handles nested tags and entities correctly
- [Phase 03-ai-pipeline]: Pin anthropic==0.86.0 exact version in requirements.txt for reproducible CI
- [Phase 03-ai-pipeline]: 12 generate_exercises tests use ModuleNotFoundError as RED signal before GREEN implementation
- [Phase 03-ai-pipeline]: catch broad Exception (not just anthropic.APIError) in call_claude to match test mock using Exception side_effect
- [Phase 03-ai-pipeline]: anthropic.Anthropic() instantiated inside call_claude() function not at module level — enables clean patching in tests

### Pending Todos

None yet.

### Blockers/Concerns

- [Phase 2]: Verify live VOA RSS feed URL and feedparser field names before coding fetcher — URL has changed historically; store in plan/config.json not hardcoded
- [Phase 3]: Verify current anthropic SDK version on PyPI; verify claude-3-5-haiku-20241022 model ID against Anthropic docs before pinning in requirements.txt

## Session Continuity

Last session: 2026-03-23T01:42:49.561Z
Stopped at: Completed 03-ai-pipeline-02-PLAN.md
Resume file: None
