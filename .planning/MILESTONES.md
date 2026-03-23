# Milestones

## v1.1 Dual AI Provider (Shipped: 2026-03-23)

**Phases completed:** 3 phases (4-6), 5 plans

**Key accomplishments:**
1. `scripts/ai_provider.py` — TDD-built provider dispatcher with `resolve_provider` + `call_ai`, routing Claude/OpenAI calls via env var or `plan/config.json`
2. `tests/test_ai_provider.py` — 11-test suite covering all provider paths with mocked API calls (zero live requests)
3. `generate_exercises.py` wired to `call_ai`; `plan/config.json` gains `ai_provider` + `openai_model` fields; CI workflow gets `OPENAI_API_KEY` secret
4. `ProviderError` exception with automatic single-retry fallback — primary outage retries backup provider, both-fail exits 1 to CI stderr
5. `docs/ai-providers.md` — bilingual step-by-step guide covering OpenAI key, Anthropic key, GitHub Secrets setup, and `AI_PROVIDER` priority rule
6. `docs/configuration.md` + `docs/setup-guide.md` updated with `OPENAI_API_KEY` row and cross-link to ai-providers.md

**Stats:**
- LOC: ~2,153 Python (scripts + tests)
- Timeline: 2026-03-20 → 2026-03-23 (3 days)
- Tests: 115 passing (zero regressions)
- Git range: `docs: create milestone v1.1 roadmap` → `docs(phase-06): complete phase execution`

---

## v1.0 MVP (Shipped: 2026-03-23)

**Phases completed:** 3 phases, 7 plans, 0 tasks

**Key accomplishments:**
1. CI foundation with timezone-correct Beijing date derivation, idempotency guard, and GitHub Actions write permissions
2. RSS fetch pipeline: VOA Special English primary + BBC Learning English fallback, Article Envelope JSON output
3. AI exercise generation via Claude API (claude-3-5-haiku-20241022) producing vocabulary, chunking expressions, and comprehension Q&A
4. Four-section Markdown lesson committed daily to `content/YYYY-MM-DD.md` via three-stage pipeline with `set -eo pipefail`
5. TDD throughout: 12 unit tests for RSS fetch, 12 for exercise generation, all passing in CI
6. First live lesson committed: `content/2026-03-23.md`

**Stats:**
- LOC: ~1,750 Python (scripts + tests)
- Timeline: 2026-03-20 → 2026-03-23 (3 days)
- Git range: feat(01-01) → feat(03-03)

---
