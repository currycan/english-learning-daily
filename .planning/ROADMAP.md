# Roadmap: English Daily Content

## Overview

Three phases deliver an automated daily English learning pipeline. Phase 1 establishes the CI foundation — git commit from Actions, timezone-correct date derivation, idempotency guard, and the shared utilities module. Phase 2 builds the RSS fetch stage with VOA primary and BBC fallback, producing a validated Article Envelope. Phase 3 completes the pipeline by adding AI exercise generation via Claude API and the Markdown renderer, delivering a committed daily lesson file end-to-end.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Foundation** - CI scaffold, shared utilities, git commit, and timezone/idempotency infrastructure (completed 2026-03-22)
- [ ] **Phase 2: RSS Fetch** - Article fetching from VOA/BBC RSS with validation and Article Envelope output
- [ ] **Phase 3: AI Pipeline** - AI exercise generation, Markdown rendering, and complete end-to-end pipeline

## Phase Details

### Phase 1: Foundation
**Goal**: CI infrastructure is ready to commit content files from GitHub Actions with correct Beijing date, write permissions, and idempotency protection
**Depends on**: Nothing (first phase)
**Requirements**: CI-01, CI-02
**Success Criteria** (what must be TRUE):
  1. GitHub Actions workflow runs on cron schedule and can be triggered manually via `workflow_dispatch`
  2. A test run commits a placeholder file to `content/` with the correct Beijing-date filename (YYYY-MM-DD.md)
  3. Running the workflow twice on the same day does not create a duplicate commit — the second run exits 0 cleanly
  4. A simulated failure (non-zero script exit) causes the CI job to be marked failed in GitHub Actions
**Plans**: 2 plans

Plans:
- [ ] 01-01-PLAN.md — shared utilities: get_beijing_date(), content_path(), Beijing TZ constants (TDD)
- [ ] 01-02-PLAN.md — commit_content.py placeholder + idempotency guard + daily-content.yml CI workflow (TDD + auto)

### Phase 2: RSS Fetch
**Goal**: The system reliably fetches one real English article per day from VOA Special English (BBC fallback), validates it, and emits a well-formed Article Envelope JSON
**Depends on**: Phase 1
**Requirements**: FTCH-01, FTCH-02, FTCH-03
**Success Criteria** (what must be TRUE):
  1. Running `python -m scripts.fetch_article` prints a JSON object containing `title`, `body`, and `source_url` fields populated from a live VOA RSS feed
  2. When the VOA feed is unavailable (simulated), the script falls back to BBC Learning English and still emits a valid Article Envelope
  3. When both feeds fail, the script exits non-zero with a clear error message
  4. The emitted article body is at least 200 characters and contains natural English prose (not feed metadata or HTML tags)
**Plans**: 2 plans

Plans:
- [ ] 02-01-PLAN.md — TDD scaffold: 12 failing tests + feedparser dependency + config feed URLs (RED phase)
- [ ] 02-02-PLAN.md — Implementation: scripts/feed_article.py with all 8 functions (GREEN phase)

### Phase 3: AI Pipeline
**Goal**: Every day a complete English lesson Markdown file is committed to `content/YYYY-MM-DD.md` — containing the real article, 5-8 vocabulary entries, chunking expressions, and comprehension questions with answers
**Depends on**: Phase 2
**Requirements**: AIGEN-01, AIGEN-02, AIGEN-03, AIGEN-04, OUT-01, OUT-02, OUT-03
**Success Criteria** (what must be TRUE):
  1. Running the full pipeline end-to-end produces a committed `content/YYYY-MM-DD.md` file in the repository using Beijing date
  2. The committed file contains four clearly separated sections: article text with source URL, vocabulary (5-8 words with definitions and in-article examples), chunking expressions (with Chinese meanings and 2+ usage examples each), and comprehension questions with answers
  3. The comprehension questions section contains at least one inferential question (not purely factual recall)
  4. If the Claude API call fails, the pipeline exits non-zero and no partial file is committed
**Plans**: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation | 2/2 | Complete   | 2026-03-22 |
| 2. RSS Fetch | 0/2 | Not started | - |
| 3. AI Pipeline | 0/TBD | Not started | - |
