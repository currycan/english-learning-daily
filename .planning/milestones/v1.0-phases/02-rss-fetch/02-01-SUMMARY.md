---
phase: 02-rss-fetch
plan: 01
subsystem: testing
tags: [feedparser, rss, tdd, red-phase, pytest, unit-tests]

# Dependency graph
requires:
  - phase: 01-foundation
    provides: content_utils (get_beijing_date, content_path), scripts package structure, test infrastructure
provides:
  - 12 failing unit tests for scripts/feed_article.py covering FTCH-01/02/03
  - feedparser==6.0.12 pinned in requirements.txt
  - plan/config.json content_feeds config with verified newsinlevels.com primary URL
affects:
  - 02-rss-fetch plan 02 (GREEN implementation driven by these tests)

# Tech tracking
tech-stack:
  added: [feedparser==6.0.12]
  patterns: [TDD RED phase — test contracts written before implementation, feedparser.parse mock pattern via unittest.mock.patch]

key-files:
  created: [tests/test_feed_article.py]
  modified: [requirements.txt, plan/config.json]

key-decisions:
  - "newsinlevels.com/feed is the ONLY verified primary URL returning 800+ char body via content:encoded (tested 2026-03-23)"
  - "BBC Learning English fallback retained per locked user decision despite <165 char returns; retry logic handles gracefully"
  - "feedparser chosen over xml.etree for RSS — handles malformed XML and CDATA blocks"

patterns-established:
  - "feedparser mock pattern: patch feedparser.parse to return MagicMock with .bozo=False and .entries=[...]"
  - "_make_entry() factory function for creating test feedparser entry dicts with optional content[0].value"
  - "LONG_BODY sentinel = 'This is a long article body. ' * 10 (300+ chars, exceeds 200-char validation threshold)"

requirements-completed: [FTCH-01, FTCH-02, FTCH-03]

# Metrics
duration: 8min
completed: 2026-03-22
---

# Phase 02 Plan 01: RSS Fetch RED Phase Summary

**12 failing unit tests for feed_article.py written using feedparser mock patterns, with newsinlevels.com verified as primary feed URL in config**

## Performance

- **Duration:** ~8 min
- **Started:** 2026-03-22T17:02:00Z
- **Completed:** 2026-03-22T17:10:08Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments

- Added feedparser==6.0.12 to requirements.txt and installed in project venv
- Updated plan/config.json with content_feeds block (primary_url=newsinlevels.com, fallback_url=BBC, 7 content_topics)
- Wrote all 12 unit tests for FTCH-01/02/03 — all fail with ModuleNotFoundError confirming RED phase

## Task Commits

Each task was committed atomically:

1. **Task 1: Add feedparser dependency and update config.json** - `b978928` (chore)
2. **Task 2: Write 12 failing tests for feed_article.py (RED phase)** - `f8b4817` (test)

## Files Created/Modified

- `tests/test_feed_article.py` - 12 unit tests covering _fetch_feed, _select_entry, _try_entries, _extract_body, clean_html, _validate, fetch_article, main() — all failing RED
- `requirements.txt` - Added feedparser==6.0.12
- `plan/config.json` - Added content_feeds with primary_url, fallback_url, content_topics

## Decisions Made

- newsinlevels.com/feed confirmed as ONLY reliable primary source: returns 800+ character body text via content:encoded field
- BBC Learning English fallback kept per locked user decision; implementation will handle gracefully if it also returns short content
- feedparser==6.0.12 pinned for reproducibility across local and CI environments

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- pip install blocked by externally-managed Python environment (macOS Homebrew constraint) — resolved by using project's existing `.venv/bin/pip` instead.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Plan 02-02 (GREEN implementation) can begin: `scripts/feed_article.py` must be created to make all 12 tests pass
- Test contracts fully specify the function signatures: `_fetch_feed(url)`, `_select_entry(entries, topics)`, `_try_entries(entries, topics, max_attempts)`, `_extract_body(entry)`, `clean_html(html)`, `_validate(envelope)`, `fetch_article(config)`, `main()`
- Minimum body length for validation: 200 characters

---
*Phase: 02-rss-fetch*
*Completed: 2026-03-22*
