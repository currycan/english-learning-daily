---
phase: 03-lesson-reading-experience
plan: 01
type: execute
subsystem: website-frontend
tags: [vitest, lesson-parser, homepage, tdd]
dependencies:
  requires: [astro-content-collections, tailwind-css-4]
  provides: [lesson-parser-library, homepage-reading-experience]
  affects: [website-build-pipeline]
tech_stack:
  added: [vitest-4.1.1]
  patterns: [tdd-red-green-refactor, pure-functions, immutable-data]
key_files:
  created:
    - website/vitest.config.ts
    - website/src/lib/lesson-parser.ts
    - website/src/lib/lesson-parser.test.ts
  modified:
    - website/package.json
    - website/src/pages/index.astro
decisions:
  - Used word-boundary truncation for extractPreview to match test expectations
  - Implemented collapsible sections using CSS grid-template-rows animation
  - Parser functions are pure and immutable as per CLAUDE.md constraints
  - TDD approach with 15 comprehensive test cases using real content data
  - Manual parsing of vocabulary/expressions sections for rich UI rendering
metrics:
  duration_seconds: 436
  completed_date: 2026-03-24T10:19:01Z
  tasks_completed: 2
  files_created: 3
  files_modified: 2
  test_coverage: 15_tests_passing
---

# Phase 3 Plan 1: Vitest and Parser Foundation Summary

**One-liner:** Vitest test infrastructure with comprehensive lesson-parser library enabling homepage featured lesson display and recent list.

## Tasks Completed

| Task | Description | Commit | Files | Status |
|------|-------------|--------|-------|--------|
| 1 | Install Vitest and create lesson-parser library with tests (TDD) | 6c983f0 | lesson-parser.ts, lesson-parser.test.ts, vitest.config.ts | ✅ Complete |
| 2 | Rewrite homepage with featured lesson inline and recent list | 6408da2 | index.astro | ✅ Complete |

## What Was Built

### Lesson Parser Library
- **parseSections()** - Splits markdown into 4 sections (article, vocabulary, expressions, comprehension)
- **extractSourceUrl()** - Finds source URL from `> Source:` pattern in article
- **extractPreview()** - Gets first sentence preview with word-boundary truncation
- **parseComprehension()** - Parses Q&A blocks with regex for structured data
- **getTodayShanghai()** - Returns current date in Asia/Shanghai timezone as YYYY-MM-DD

All functions are pure, immutable, and comprehensively tested with 15 test cases using real content from `content/2026-03-24.md`.

### Homepage Reading Experience
- **Featured lesson display** - Shows today's lesson or most recent, full inline with article text always visible
- **Notice bar** - Build-time conditional warning "⚠️ 今日课文将在中午更新" when today's lesson missing
- **Collapsible sections** - 📚 词汇, 🔗 表达, ❓ 理解 with CSS grid animation and chevron rotation
- **Tap-to-reveal answers** - Q&A blocks with "查看答案" buttons for progressive disclosure
- **Recent lessons list** - 5 most recent lessons with date + preview links using proper BASE_URL prefix
- **Vocabulary/expression parsing** - Rich UI cards with word definitions, POS tags, Chinese gloss, quotes, examples

## Technical Achievements

### Test-Driven Development
Successfully followed TDD RED-GREEN-REFACTOR cycle:
1. **RED**: Created 15 failing tests with real content fixtures
2. **GREEN**: Implemented parser functions to pass all tests
3. **REFACTOR**: Refined extractPreview truncation logic for word boundaries

### Build Integration
- Vitest configured with `include: ['src/**/*.test.ts']`
- Test scripts added: `npm test` and `npm test:watch`
- Build pipeline validates with `npm run build` - no errors
- Static site generates successfully with lesson content

### UI Compliance
- **LESS-01**: Homepage shows featured lesson with full article text
- **LESS-02**: Recent lessons list (5 items) with date + preview
- **LESS-03**: Notice bar conditional logic for missing today lesson
- **Accessibility**: 44px min-height tap targets throughout
- **GitHub Pages**: Correct BASE_URL prefix for `/study-all/` deployment

## Deviations from Plan

**Auto-fixed Issues:**

**1. [Rule 1 - Bug] Fixed extractPreview truncation behavior**
- **Found during:** Task 1 GREEN phase
- **Issue:** Initial character-count truncation broke words mid-sentence, failing tests
- **Fix:** Implemented word-boundary detection to truncate at complete words
- **Files modified:** website/src/lib/lesson-parser.ts
- **Commit:** 6c983f0 (part of TDD cycle)

## Verification Results

### Automated Tests
```bash
✓ 15 tests passing (all parser functions)
✓ Build succeeds without errors
✓ Static routes generate correctly (/index.html, /lesson/2026-03-24/index.html)
```

### Manual Acceptance Criteria
- [x] Vitest installed and configured
- [x] Parser library exports 5 functions with interfaces
- [x] Homepage imports from lesson-parser and uses getTodayShanghai()
- [x] Notice bar styling and copy matches spec
- [x] Collapsible sections with proper data attributes
- [x] Recent lessons limited to 5 items (.slice(0, 5))
- [x] BASE_URL prefix for GitHub Pages links
- [x] 44px min-height tap targets throughout

## Known Stubs

None - all functionality fully implemented and wired with real data flow from content collections through parser to UI rendering.

## Self-Check: PASSED

**Created files exist:**
- ✓ website/vitest.config.ts
- ✓ website/src/lib/lesson-parser.ts
- ✓ website/src/lib/lesson-parser.test.ts

**Commits exist:**
- ✓ 6c983f0: Task 1 - Vitest + parser library + tests
- ✓ 6408da2: Task 2 - Homepage implementation

**Build validation:**
- ✓ `npm run build` succeeds
- ✓ All parser tests pass
- ✓ Homepage renders with real lesson content