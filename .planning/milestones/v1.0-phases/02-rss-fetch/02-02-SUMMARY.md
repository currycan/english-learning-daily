---
phase: 02-rss-fetch
plan: 02
subsystem: api
tags: [feedparser, rss, html-parsing, json, idempotency]

# Dependency graph
requires:
  - phase: 02-01
    provides: "12 unit tests specifying all 8 function contracts for feed_article.py"
  - phase: 01-foundation
    provides: "content_utils.py with get_beijing_date() and content_path()"
provides:
  - "scripts/feed_article.py — complete RSS fetch module with primary/fallback cascade"
  - "8 public functions: clean_html, _extract_body, _validate, _fetch_feed, _select_entry, _try_entries, fetch_article, main"
  - "stdout JSON envelope: {title, body, source_url} for Phase 3 consumption"
affects: [03-content-gen]

# Tech tracking
tech-stack:
  added: [feedparser]
  patterns:
    - "_TextExtractor HTMLParser subclass for tag-stripping without regex"
    - "Primary → fallback feed cascade with per-entry retry up to max_attempts"
    - "Idempotency guard via content_path(today).exists() check before network call"

key-files:
  created:
    - scripts/feed_article.py
  modified: []

key-decisions:
  - "Used HTMLParser subclass (_TextExtractor) instead of regex for HTML cleaning — handles nested tags and entities correctly"
  - "id() used for deduplication in _try_entries candidate list — safe because feedparser entries are unique objects in-memory"
  - "No error handling on _load_config() — missing config is a fatal programmer error, letting Python raise naturally is correct"

patterns-established:
  - "Pattern: _try_entries builds ordered candidates list (preferred first, then remaining) to minimize network retries"
  - "Pattern: feed_article errors print to stderr with ERROR:/WARNING: prefix, clean stdout reserved for JSON envelope"

requirements-completed: [FTCH-01, FTCH-02, FTCH-03]

# Metrics
duration: 3min
completed: 2026-03-22
---

# Phase 2 Plan 02: RSS Fetch Implementation Summary

**feedparser-based RSS article fetcher with primary/fallback cascade, 3-entry retry, HTMLParser tag-stripping, and idempotency guard writing {title, body, source_url} JSON to stdout**

## Performance

- **Duration:** 3 min
- **Started:** 2026-03-22T17:09:54Z
- **Completed:** 2026-03-22T17:12:54Z
- **Tasks:** 1
- **Files modified:** 1

## Accomplishments

- Implemented all 8 required public functions in scripts/feed_article.py (185 lines)
- 12/12 unit tests pass (GREEN phase complete); full 77-test suite still clean
- Primary feed tried first, fallback triggered only on empty/invalid; exits 1 with ERROR: when both fail

## Task Commits

Each task was committed atomically:

1. **Task 1: Implement scripts/feed_article.py with all 8 required functions** - `8fe3cce` (feat)

## Files Created/Modified

- `scripts/feed_article.py` - Complete RSS fetch module: 8 public functions, HTMLParser tag-stripping, feedparser integration, stdout JSON output

## Decisions Made

- Used HTMLParser subclass instead of regex for HTML tag stripping — more robust against nested tags and edge cases in RSS feeds
- Used `id()` for in-memory deduplication in `_try_entries` candidate ordering — feedparser entries are unique objects so this is safe and avoids mutating the input list
- Kept `_load_config()` without try/except — missing plan/config.json is a programmer error that should surface immediately

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- scripts/feed_article.py is importable and tested, ready for Phase 3 (content generation) to consume via `python -m scripts.feed_article | python -m scripts.generate_content`
- feedparser installed in .venv and present in requirements
- No blockers

---
*Phase: 02-rss-fetch*
*Completed: 2026-03-22*
