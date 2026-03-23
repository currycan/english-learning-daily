# Milestones

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

