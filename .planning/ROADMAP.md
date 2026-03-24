# Roadmap: English Daily Content

## Milestones

- ✅ **v1.0 MVP** — Phases 1-3 (shipped 2026-03-23)
- ✅ **v1.1 Dual AI Provider** — Phases 4-6 (shipped 2026-03-23)
- ✅ **v1.2 Third-Party Claude API** — Phases 7-8 (shipped 2026-03-23)

## Phases

<details>
<summary>✅ v1.0 MVP (Phases 1-3) — SHIPPED 2026-03-23</summary>

- [x] Phase 1: Foundation (2/2 plans) — completed 2026-03-22
- [x] Phase 2: RSS Fetch (2/2 plans) — completed 2026-03-22
- [x] Phase 3: AI Pipeline (3/3 plans) — completed 2026-03-23

Full archive: `.planning/milestones/v1.0-ROADMAP.md`

</details>

<details>
<summary>✅ v1.1 Dual AI Provider (Phases 4-6) — SHIPPED 2026-03-23</summary>

- [x] Phase 4: Provider Abstraction + OpenAI Integration (2/2 plans) — completed 2026-03-23
- [x] Phase 5: Fallback Logic (1/1 plan) — completed 2026-03-23
- [x] Phase 6: AI Provider Documentation (2/2 plans) — completed 2026-03-23

Full archive: `.planning/milestones/v1.1-ROADMAP.md`

</details>

<details>
<summary>✅ v1.2 Third-Party Claude API (Phases 7-8) — SHIPPED 2026-03-23</summary>

- [x] Phase 7: Custom Endpoint Implementation (3/3 plans) — completed 2026-03-23
- [x] Phase 8: Third-Party Provider Documentation (1/1 plan) — completed 2026-03-23

Full archive: `.planning/milestones/v1.2-ROADMAP.md`

</details>

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Foundation | v1.0 | 2/2 | Complete | 2026-03-22 |
| 2. RSS Fetch | v1.0 | 2/2 | Complete | 2026-03-22 |
| 3. AI Pipeline | v1.0 | 3/3 | Complete | 2026-03-23 |
| 4. Provider Abstraction + OpenAI Integration | v1.1 | 2/2 | Complete | 2026-03-23 |
| 5. Fallback Logic | v1.1 | 1/1 | Complete | 2026-03-23 |
| 6. AI Provider Documentation | v1.1 | 2/2 | Complete | 2026-03-23 |
| 7. Custom Endpoint Implementation | v1.2 | 3/3 | Complete | 2026-03-23 |
| 8. Third-Party Provider Documentation | v1.2 | 1/1 | Complete | 2026-03-23 |

### Phase 1: Gemini Migration

**Goal:** Replace all Claude/OpenAI code, config, CI, tests, and docs with Gemini-only implementation using google-genai SDK
**Requirements**: TBD
**Depends on:** Phase 0
**Plans:** 2 plans

Plans:
- [x] 01-01-PLAN.md — Replace production code, config, and CI with Gemini-only
- [ ] 01-02-PLAN.md — Rewrite tests and documentation for Gemini
