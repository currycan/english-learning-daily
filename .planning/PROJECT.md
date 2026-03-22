# English Daily Content

## What This Is

An automated system that fetches a real English article from public sources (VOA, BBC, or similar) each day, uses AI to generate B1-B2 level companion exercises (vocabulary highlights and comprehension questions), and commits the combined content as a date-named Markdown file to git. The goal is a growing personal library of learning materials readable directly from the repository.

## Core Value

Every day a ready-to-read English lesson lands in git — real content, not generated filler, with targeted vocabulary and exercises to deepen understanding.

## Requirements

### Validated

- ✓ Daily GitHub Actions scheduling (morning/evening) — existing
- ✓ Bark push notification delivery — existing
- ✓ State tracking in `plan/state.json` — existing
- ✓ Python script pipeline architecture (stdout→stdin JSON) — existing
- ✓ Git commit automation from CI — existing

### Active

- [ ] Fetch one English article per day from a public RSS/API source (VOA Special English or BBC Learning English)
- [ ] Filter articles to B1-B2 reading level (short sentences, common vocabulary)
- [ ] Use AI (Claude API) to extract 5–8 key vocabulary words with definitions and example sentences
- [ ] Use AI to generate 3–5 comprehension questions with answers
- [ ] Combine article + vocabulary + questions into a single Markdown file
- [ ] Commit file to `content/YYYY-MM-DD.md` via GitHub Actions daily
- [ ] Skip duplicate commits if article already exists for that date
- [ ] Handle source fetch failures gracefully (fallback or retry)

### Out of Scope

- Push notifications for content (separate system, not needed here) — user reads directly from git
- Interactive exercises or quizzes — static Markdown only for v1
- Multiple articles per day — one focused lesson is better than overwhelm
- Audio or video content — text only for v1
- User progress tracking for this content — separate concern

## Context

The repository already has a working GitHub Actions + Python pipeline for push notifications. The new content generation system will follow the same architectural patterns (modular Python scripts, CI-triggered, git-committed output) but targets a different output: static learning files instead of push payloads.

Content sources with no auth required:
- **VOA Learning English** — RSS at `feeds.voanews.com/learningenglish/english` — designed for non-native speakers
- **BBC Learning English** — RSS available, B1-B2 content
- **The Guardian** — public API with free tier, rich article content

AI generation will use the Claude API (Anthropic) to ensure consistent, high-quality exercises without depending on fragile scraped content.

## Constraints

- **Tech stack**: Python (matches existing codebase), no new runtime dependencies beyond `requests` and `anthropic` SDK
- **API costs**: Claude API usage must be minimal — one call per day, short prompt
- **No secrets in code**: `ANTHROPIC_API_KEY` from GitHub Secrets only
- **File format**: Pure Markdown, no frontmatter complexity, readable in any git viewer
- **CI**: GitHub Actions (existing infrastructure)

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| VOA Special English as primary source | Explicitly designed for B1-B2 learners, free RSS, stable | — Pending |
| Claude API for exercise generation | Already available in this project's ecosystem, high quality | — Pending |
| One file per day in `content/` | Simple, browsable, no database needed | — Pending |
| Markdown only (no HTML/JSON) | Readable anywhere git is viewable | — Pending |

---
*Last updated: 2026-03-22 after initialization*
