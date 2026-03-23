# Roadmap: English Daily Content

## Milestones

- ✅ **v1.0 MVP** — Phases 1-3 (shipped 2026-03-23)
- 🚧 **v1.1 Dual AI Provider** — Phases 4-6 (in progress)

## Phases

<details>
<summary>✅ v1.0 MVP (Phases 1-3) — SHIPPED 2026-03-23</summary>

- [x] Phase 1: Foundation (2/2 plans) — completed 2026-03-22
- [x] Phase 2: RSS Fetch (2/2 plans) — completed 2026-03-22
- [x] Phase 3: AI Pipeline (3/3 plans) — completed 2026-03-23

Full archive: `.planning/milestones/v1.0-ROADMAP.md`

</details>

### 🚧 v1.1 Dual AI Provider (In Progress)

**Milestone Goal:** Support both Claude and OpenAI as interchangeable content generation backends, with automatic fallback on failure.

- [ ] **Phase 4: Provider Abstraction + OpenAI Integration** — Unified provider interface, env var + config switching, OpenAI gpt-4o-mini producing identical output, unit tests for OpenAI path
- [ ] **Phase 5: Fallback Logic** — Automatic provider fallback on API failure, CI-visible fallback logging, unit tests for fallback scenarios
- [ ] **Phase 6: AI Provider Documentation** — Configuration guide covering both API keys, GitHub Secrets setup, and provider switching rules

## Phase Details

### Phase 4: Provider Abstraction + OpenAI Integration
**Goal**: Users can switch between Claude and OpenAI via a single env var or config entry, and the system produces identical lesson output from either provider
**Depends on**: Phase 3
**Requirements**: PRVD-01, PRVD-02, PRVD-03, OAPI-01, OAPI-02, OAPI-03, TEST-01
**Success Criteria** (what must be TRUE):
  1. Setting `AI_PROVIDER=openai` causes the pipeline to call OpenAI instead of Claude and produce a valid four-section lesson file
  2. Setting `AI_PROVIDER=anthropic` (or leaving it unset with `ai_provider: anthropic` in config.json) calls Claude as before
  3. `plan/config.json` field `ai_provider` controls the default provider when the env var is absent
  4. The OpenAI model used is configurable via `plan/config.json` (defaults to `gpt-4o-mini`)
  5. Unit tests for the OpenAI provider path pass with the API call mocked; `OPENAI_API_KEY` is never present in source code or config files
**Plans**: 2 plans

Plans:
- [ ] 04-01-PLAN.md — Create scripts/ai_provider.py with provider logic + tests (TDD)
- [ ] 04-02-PLAN.md — Wire generate_exercises.py to call_ai; update config, requirements, CI workflow

### Phase 5: Fallback Logic
**Goal**: A single primary provider failure does not break the daily lesson — the system automatically retries with the backup provider and records what happened
**Depends on**: Phase 4
**Requirements**: FALL-01, FALL-02, FALL-03, TEST-02
**Success Criteria** (what must be TRUE):
  1. When the primary provider raises an API error, the pipeline retries exactly once with the backup provider and succeeds if the backup responds
  2. When both providers fail, the script exits non-zero and the CI job is marked failed (identical behavior to v1.0)
  3. The CI log contains a fallback notice that names both the failed provider and the reason before the backup attempt
  4. Unit tests cover the primary-fails-backup-succeeds scenario and the both-fail scenario
**Plans**: TBD

### Phase 6: AI Provider Documentation
**Goal**: Any developer can look up `docs/ai-providers.md` and independently configure either provider with zero prior knowledge of the project
**Depends on**: Phase 5
**Requirements**: DOCS-01, DOCS-02, DOCS-03, DOCS-04
**Success Criteria** (what must be TRUE):
  1. `docs/ai-providers.md` exists and contains step-by-step instructions for obtaining an OpenAI API key from platform.openai.com
  2. The document contains step-by-step instructions for obtaining an Anthropic API key from console.anthropic.com
  3. The document explains how to store `OPENAI_API_KEY` and `ANTHROPIC_API_KEY` as GitHub Actions Repository Secrets
  4. The document states the priority rule: `AI_PROVIDER` env var overrides `ai_provider` in `plan/config.json`
**Plans**: TBD

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Foundation | v1.0 | 2/2 | Complete | 2026-03-22 |
| 2. RSS Fetch | v1.0 | 2/2 | Complete | 2026-03-22 |
| 3. AI Pipeline | v1.0 | 3/3 | Complete | 2026-03-23 |
| 4. Provider Abstraction + OpenAI Integration | v1.1 | 0/2 | Not started | - |
| 5. Fallback Logic | v1.1 | 0/TBD | Not started | - |
| 6. AI Provider Documentation | v1.1 | 0/TBD | Not started | - |
