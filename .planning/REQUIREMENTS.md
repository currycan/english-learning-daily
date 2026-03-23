# Requirements: English Daily Content

**Defined:** 2026-03-22
**Core Value:** Every day a ready-to-read English lesson lands in git — real content with targeted vocabulary, chunking expressions, and exercises to deepen understanding.

## v1 Requirements

### Fetch

- [x] **FTCH-01**: System fetches one article daily from VOA Special English RSS feed
- [x] **FTCH-02**: System falls back to BBC Learning English RSS if VOA fetch fails
- [x] **FTCH-03**: System extracts article title, full body text, and source URL from the feed

### AI Generation

- [x] **AIGEN-01**: AI extracts 5–8 key vocabulary words from the article with plain-English definitions and original example sentences taken directly from the article text
- [x] **AIGEN-02**: AI extracts 3–5 chunking expressions (natural English phrases and collocations) from the article, each with Chinese meaning and at least 2 usage examples showing the chunk in varied contexts
- [x] **AIGEN-03**: AI generates 3–5 comprehension questions covering both factual recall and inference
- [x] **AIGEN-04**: AI generates answers for all comprehension questions

### Output

- [x] **OUT-01**: System renders a Markdown file with four clearly delimited sections: full article text + source URL → vocabulary → chunking expressions → comprehension questions + answers
- [x] **OUT-02**: File is named `content/YYYY-MM-DD.md` using Beijing time (CST, UTC+8) regardless of the CI runner's timezone
- [x] **OUT-03**: System commits and pushes the rendered file to git via GitHub Actions on each successful run

### CI Workflow

- [x] **CI-01**: GitHub Actions workflow runs on a daily cron schedule
- [x] **CI-02**: Pipeline exits non-zero and marks the CI job failed if RSS fetch or AI generation fails

## v2 Requirements

### Content Quality

- **QUAL-01**: Topic tagging (science, health, education, etc.) added to file header
- **QUAL-02**: Vocabulary reuse detection — skip words already seen in previous N files
- **QUAL-03**: CEFR word-level annotation on vocabulary entries (A2/B1/B2)

### Operational

- **OPS-01**: Idempotency guard — skip commit if today's file already exists
- **OPS-02**: Weekly digest: auto-generated `content/week-NN.md` summarizing the week's vocabulary and chunks

## Out of Scope

| Feature | Reason |
|---------|--------|
| Push notifications for content | Separate system; user reads from git directly |
| Interactive exercises / quiz UI | Static Markdown only; no web app |
| Multiple articles per day | One focused lesson beats information overload |
| Audio or video content | Text only for v1 |
| Grammar exercises | Chunking + comprehension sufficient for B1-B2 target |
| User progress tracking | Out of scope; no state tracking for content consumption |
| Web scraping (non-RSS) | RSS-only keeps implementation stable and legal |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| CI-01 | Phase 1 | Complete |
| CI-02 | Phase 1 | Complete |
| FTCH-01 | Phase 2 | Complete |
| FTCH-02 | Phase 2 | Complete |
| FTCH-03 | Phase 2 | Complete |
| AIGEN-01 | Phase 3 | Complete |
| AIGEN-02 | Phase 3 | Complete |
| AIGEN-03 | Phase 3 | Complete |
| AIGEN-04 | Phase 3 | Complete |
| OUT-01 | Phase 3 | Complete |
| OUT-02 | Phase 3 | Complete |
| OUT-03 | Phase 3 | Complete |

**Coverage:**
- v1 requirements: 12 total
- Mapped to phases: 12
- Unmapped: 0 ✓

---
*Requirements defined: 2026-03-22*
*Last updated: 2026-03-22 after roadmap creation*
