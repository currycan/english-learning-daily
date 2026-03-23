# Project Retrospective

*A living document updated after each milestone. Lessons feed forward into future planning.*

## Milestone: v1.0 — MVP

**Shipped:** 2026-03-23
**Phases:** 3 | **Plans:** 7 | **Timeline:** 3 days (2026-03-20 → 2026-03-23)

### What Was Built

- CI foundation: `content_utils.py` (Beijing timezone, content_path), `commit_content.py` (idempotency guard), `daily-content.yml` (cron + write permissions)
- RSS fetch pipeline: `feed_article.py` with VOA primary / BBC fallback cascade, Article Envelope JSON output via stdout
- AI exercise generation: `generate_exercises.py` calling Claude API for vocabulary, chunking expressions, and comprehension Q&A
- Three-stage pipe: `feed_article.py | generate_exercises.py | commit_content.py` with `set -eo pipefail`
- 24 unit tests across all three stages (12 feed + 12 exercise), all passing

### What Worked

- TDD RED → GREEN per plan kept scope tight — each plan had a single clear deliverable
- Separating the pipeline into three scripts communicating via JSON stdout/stdin made each stage independently testable
- GSD phase structure matched naturally to the pipeline stages (Foundation → Fetch → AI)
- Pinning exact dependency versions (feedparser==6.0.12, anthropic==0.86.0) prevented CI surprises

### What Was Inefficient

- Primary RSS URL required research to discover newsinlevels.com/feed — VOA's documented URL didn't return full body text; this could have been validated earlier in a research phase
- anthropic SDK required a mid-development version check to pin the correct model ID (claude-3-5-haiku-20241022)
- Broad Exception catch in call_claude() is a minor code smell — should be anthropic.APIError specifically

### Patterns Established

- `set -eo pipefail` + three-stage pipe pattern for multi-script CI pipelines
- `datetime.now(tz=BEIJING_TZ).date()` (not `date.today()`) for timezone-correct CI date derivation
- Instantiate SDK clients inside functions (not at module level) for clean test patchability
- Idempotency guard via `path.exists()` + `sys.exit(0)` — zero CI noise on duplicate runs

### Key Lessons

1. Verify live RSS feed URLs in research phase before writing a single test — URL formats change and `feedparser` silently returns empty entries for wrong URLs
2. Module-level SDK client instantiation is an anti-pattern for testability; always inject or instantiate inside the function under test
3. `set -eo pipefail` is non-optional for piped CI commands — without it, a failing middle stage passes silently

### Cost Observations

- Model mix: ~0% opus, ~80% sonnet, ~20% haiku
- Sessions: ~6 (research, plan per phase, execution)
- Notable: claude-3-5-haiku for daily content generation keeps API costs minimal at ~1,400 tokens/day

---

## Milestone: v1.1 — Dual AI Provider

**Shipped:** 2026-03-23
**Phases:** 3 (4-6) | **Plans:** 5 | **Timeline:** same day as v1.0

### What Was Built

- `scripts/ai_provider.py` — provider abstraction with `resolve_provider`, `call_claude`, `call_openai`, `call_ai` dispatcher
- `ProviderError` exception + `_dispatch` helper for automatic single-retry fallback; `call_ai` orchestrates primary → backup chain
- `generate_exercises.py` wired to `call_ai`; `plan/config.json` gains `ai_provider` + `openai_model`; CI workflow gains `OPENAI_API_KEY`
- `tests/test_ai_provider.py` — 11 unit tests for all provider paths; `tests/test_ai_provider_docs.py` — 7 content assertion tests
- `docs/ai-providers.md` — bilingual step-by-step guide (OpenAI key, Anthropic key, GitHub Secrets, priority rule)
- `docs/configuration.md` and `docs/setup-guide.md` updated with `OPENAI_API_KEY` row and cross-link

### What Worked

- TDD RED → GREEN per task continued to keep scope tight — each commit represents exactly one behavioral change
- The `ProviderError` + `_backup_provider` set-difference approach is clean and extensible to N providers
- Documentation phase (Phase 6) was the right call — bilingual format matches existing docs and pytest content assertions ensure correctness survives refactors
- Separating provider dispatch into `call_ai` (orchestrator) vs `call_claude`/`call_openai` (low-level) made the fallback path trivially testable

### What Was Inefficient

- The broad `Exception` catch in `call_openai` was intentional (openai SDK raises many error subtypes) but worth revisiting if SDK stabilizes
- Phase 6 content research had medium confidence on URLs — no live fetch was performed, relying on known-stable domains (platform.openai.com, console.anthropic.com)

### Patterns Established

- `ProviderError` as a thin domain exception wrapping SDK errors — keeps callers composable, avoids `sys.exit` in library functions
- `_backup_provider = (VALID_PROVIDERS - {primary}).pop()` — deterministic backup selection without hardcoding pairs
- Pytest content assertion tests for documentation — `pathlib.Path(__file__).parent.parent` fixture pattern is reusable
- Bilingual (English line + Chinese line) docs format established across all project docs

### Key Lessons

1. Documentation TDD (write assertions first, then content) catches gaps that subjective review misses — 7 failing tests immediately identified 4 missing required strings
2. `ProviderError` at the low level + fallback at the orchestrator level is the right separation — it enables testing fallback without live API calls
3. A separate documentation phase is worth it even for small projects — it surface-tested the actual UX of configuration that code review can't catch

### Cost Observations

- Model mix: ~0% opus, ~85% sonnet, ~15% haiku
- Sessions: ~4 (plan phase 4 → execute 4 → 5 → 6)
- Notable: documentation phase completed in a single session with zero rework

---

## Cross-Milestone Trends

### Process Evolution

| Milestone | Phases | Plans | Key Change |
|-----------|--------|-------|------------|
| v1.0 | 3 | 7 | First milestone — established TDD + pipe patterns |
| v1.1 | 3 | 5 | Provider abstraction + fallback; documentation TDD pattern |

### Cumulative Quality

| Milestone | Tests | Coverage | New Dependencies |
|-----------|-------|----------|-----------------|
| v1.0 | 24 | ~85% scripts | feedparser, anthropic |
| v1.1 | 115 | ~90% scripts | openai 2.29.0 |
