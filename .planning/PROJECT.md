# English Daily Content

## What This Is

An automated system that fetches a real English article from public sources each day, uses an AI provider (Claude — including third-party Claude-compatible APIs — or OpenAI, switchable via config with automatic fallback) to generate B1-B2 companion exercises (vocabulary highlights, chunking expressions, comprehension questions with answers), and commits the combined lesson as a date-named Markdown file to git. Ships daily to `content/YYYY-MM-DD.md` via GitHub Actions.

## Core Value

Every day a ready-to-read English lesson lands in git — real content, not generated filler, with targeted vocabulary, chunking expressions, and exercises to deepen understanding.

## Requirements

### Validated

- ✓ GitHub Actions daily cron scheduling — v1.0
- ✓ Git commit automation from CI with Beijing-timezone filename — v1.0
- ✓ Idempotency guard (skip duplicate commits) — v1.0
- ✓ RSS fetch from VOA Special English (primary) with BBC Learning English fallback — v1.0
- ✓ Article Envelope JSON output (title, body, source_url) — v1.0
- ✓ AI extraction of 5–8 vocabulary words with definitions and in-article examples — v1.0
- ✓ AI extraction of 3–5 chunking expressions with Chinese meanings and usage examples — v1.0
- ✓ AI generation of 3–5 comprehension questions with answers — v1.0
- ✓ Four-section Markdown lesson file (article + vocabulary + chunks + Q&A) — v1.0
- ✓ CI exits non-zero and marks job failed on fetch or AI generation failure — v1.0
- ✓ Provider abstraction layer with env var + config.json switching (PRVD-01, PRVD-02, PRVD-03) — v1.1
- ✓ OpenAI gpt-4o-mini integration with identical output format (OAPI-01, OAPI-02, OAPI-03) — v1.1
- ✓ Automatic fallback to backup provider on API failure (FALL-01, FALL-02, FALL-03) — v1.1
- ✓ AI providers configuration guide docs/ai-providers.md (DOCS-01–04) — v1.1
- ✓ OpenAI and fallback unit tests (TEST-01, TEST-02) — v1.1
- ✓ Anthropic client accepts configurable base_url and auth_token (TPROV-01, TPROV-02, TPROV-03, TPROV-04) — v1.2
- ✓ Env vars ANTHROPIC_BASE_URL and ANTHROPIC_AUTH_TOKEN at highest priority (CONF-01, CONF-02) — v1.2
- ✓ plan/config.json fields anthropic_base_url / anthropic_auth_token as lower-priority fallback (CONF-03) — v1.2
- ✓ GitHub Actions CI injects ANTHROPIC_BASE_URL and ANTHROPIC_AUTH_TOKEN from secrets (CONF-04) — v1.2
- ✓ docs/ai-providers.md bilingual third-party provider section (DOCS-01, DOCS-02, DOCS-03) — v1.2
- ✓ Unit tests for custom endpoint path and backward compat (TEST-01, TEST-02) — v1.2

### Active

(None — define next milestone goals via `/gsd:new-milestone`)

### Out of Scope

| Feature | Reason |
|---------|--------|
| Push notifications for content | Separate system; user reads from git directly |
| Interactive exercises / quiz UI | Static Markdown only; no web app |
| Multiple articles per day | One focused lesson beats information overload |
| Audio or video content | Text only |
| Grammar exercises | Chunking + comprehension sufficient for B1-B2 target |
| User progress tracking | Out of scope; no state tracking for content consumption |
| Web scraping (non-RSS) | RSS-only keeps implementation stable and legal |
| Multi-provider load balancing | Overkill for one call/day; fallback is sufficient |

## Context

**Shipped v1.2** with ~2,300 LOC Python (scripts + tests).
Tech stack: Python, feedparser 6.0.12, anthropic 0.86.0, openai 2.29.0, GitHub Actions.
First live lesson committed 2026-03-23. Dual-provider support and third-party Claude API support shipped same day.

Primary RSS source: `newsinlevels.com/feed` (only verified URL returning 800+ char bodies via `content:encoded`).
Provider switching: `AI_PROVIDER` env var > `ai_provider` in `plan/config.json` > default `anthropic`.
Third-party Claude: `ANTHROPIC_BASE_URL` + `ANTHROPIC_AUTH_TOKEN` env vars > `plan/config.json` fields > Anthropic SDK defaults.

## Constraints

- **Tech stack**: Python; `feedparser`, `anthropic`, `openai` SDK
- **API costs**: one AI call per day; gpt-4o-mini and claude-haiku are both cost-efficient
- **No secrets in code**: `ANTHROPIC_API_KEY` and `OPENAI_API_KEY` from GitHub Secrets only
- **File format**: Pure Markdown, no frontmatter, readable in any git viewer
- **CI**: GitHub Actions (existing infrastructure)

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| newsinlevels.com/feed as primary RSS | Only verified URL returning 800+ char bodies via content:encoded | ✓ Good |
| BBC Learning English as fallback | Locked user decision; feedparser handles gracefully | ✓ Good |
| claude-haiku-4-5-20251001 (pinned exact) | Cost-efficient at ~1,400 tokens/day, reproducible CI | ✓ Good |
| One AI call per day | Single structured JSON prompt covers vocab + chunks + questions | ✓ Good |
| `set -eo pipefail` in CI pipeline | Ensures pipe failures propagate — RSS failure fails CI job | ✓ Good |
| datetime.now(tz=BEIJING_TZ) not date.today() | Correctly derives Beijing date on UTC GitHub Actions runners | ✓ Good |
| Idempotency via path.exists() + sys.exit(0) | Prevents duplicate commits, clean exit on second run | ✓ Good |
| anthropic.Anthropic() inside call_claude() | Enables clean patching in unit tests without module-level state | ✓ Good |
| HTMLParser subclass for HTML cleaning | Handles nested tags and entities correctly vs regex | ✓ Good |
| TDD throughout (RED → GREEN per plan) | Caught integration issues early; all tests pass in CI | ✓ Good |
| ProviderError exception (not sys.exit) in call_claude/call_openai | Keeps low-level callers composable; fallback logic in call_ai | ✓ Good |
| _backup_provider uses set difference on VALID_PROVIDERS | Deterministic with exactly two providers; no hardcoded pairing | ✓ Good |
| openai.OpenAI() inside call_openai() | Mirrors anthropic pattern; enables clean patching in tests | ✓ Good |
| Bilingual docs format (English + Chinese per line) | Matches existing docs/setup-guide.md and docs/configuration.md style | ✓ Good |
| Conditional kwargs dict for `anthropic.Anthropic()` | Only populate `base_url`/`api_key` when non-empty — avoids overriding SDK defaults with None or empty string | ✓ Good |
| `os.environ.get() or kwarg or ''` chain for env var priority | Handles GitHub Actions empty-string secret behavior cleanly | ✓ Good |
| `ANTHROPIC_BASE_URL`/`ANTHROPIC_AUTH_TOKEN` in step-level env only | Scopes optional secrets to the generate step, not the top-level workflow env | ✓ Good |
| Summary table row format: backtick-wrap `NAME (optional)` | Allows pytest substring match `"ANTHROPIC_BASE_URL (optional)" in content` to work reliably | ✓ Good |

---
*Last updated: 2026-03-23 after v1.2 milestone*
