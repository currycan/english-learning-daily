# Roadmap: English Daily Content

## Milestones

- ✅ **v1.0 MVP** — Phases 1-3 (shipped 2026-03-23)
- ✅ **v1.1 Dual AI Provider** — Phases 4-6 (shipped 2026-03-23)
- **v1.2 Third-Party Claude API** — Phases 7-8 (active)

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

**v1.2 Third-Party Claude API**

- [x] **Phase 7: Custom Endpoint Implementation** - call_claude() accepts configurable base_url and auth_token from env vars and config.json, with tests (completed 2026-03-23)
- [ ] **Phase 8: Third-Party Provider Documentation** - docs/ai-providers.md third-party section, updated config.json example, GitHub Secrets guide

## Phase Details

### Phase 7: Custom Endpoint Implementation
**Goal**: Users can point call_claude() at any Claude-compatible third-party API endpoint by setting two env vars or config.json fields, with full backward compatibility preserved
**Depends on**: Nothing (builds on existing call_claude() in ai_provider.py)
**Requirements**: TPROV-01, TPROV-02, TPROV-03, TPROV-04, CONF-01, CONF-02, CONF-03, CONF-04, TEST-01, TEST-02
**Success Criteria** (what must be TRUE):
  1. Running with ANTHROPIC_BASE_URL and ANTHROPIC_AUTH_TOKEN env vars set causes call_claude() to pass those values to the Anthropic client constructor
  2. Running with no custom env vars or config fields behaves identically to v1.1 (no regressions)
  3. anthropic_base_url and anthropic_auth_token fields in plan/config.json are read as lower-priority fallback when env vars are absent
  4. The fallback chain (primary → backup provider) continues to work end-to-end when primary is a third-party Claude endpoint and raises ProviderError
  5. Unit tests cover both the custom-params path and the backward-compatible path, and all tests pass
**Plans**: 3 plans

Plans:
- [ ] 07-01-PLAN.md — Write three failing tests for custom endpoint behavior (TDD RED)
- [ ] 07-02-PLAN.md — Implement call_claude() extension and model_config wiring (TDD GREEN)
- [ ] 07-03-PLAN.md — Add ANTHROPIC_BASE_URL and ANTHROPIC_AUTH_TOKEN to CI workflow env block

### Phase 8: Third-Party Provider Documentation
**Goal**: A user setting up a third-party Claude-compatible API can follow docs/ai-providers.md to configure the integration end-to-end without reading source code
**Depends on**: Phase 7
**Requirements**: DOCS-01, DOCS-02, DOCS-03
**Success Criteria** (what must be TRUE):
  1. docs/ai-providers.md contains a bilingual (English + Chinese) third-party Claude section explaining ANTHROPIC_BASE_URL and ANTHROPIC_AUTH_TOKEN
  2. The config.json example in docs shows anthropic_base_url and anthropic_auth_token fields with placeholder values
  3. A GitHub Secrets section in docs covers how to add ANTHROPIC_BASE_URL and ANTHROPIC_AUTH_TOKEN as repository secrets
**Plans**: TBD

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Foundation | v1.0 | 2/2 | Complete | 2026-03-22 |
| 2. RSS Fetch | v1.0 | 2/2 | Complete | 2026-03-22 |
| 3. AI Pipeline | v1.0 | 3/3 | Complete | 2026-03-23 |
| 4. Provider Abstraction + OpenAI Integration | v1.1 | 2/2 | Complete | 2026-03-23 |
| 5. Fallback Logic | v1.1 | 1/1 | Complete | 2026-03-23 |
| 6. AI Provider Documentation | v1.1 | 2/2 | Complete | 2026-03-23 |
| 7. Custom Endpoint Implementation | 3/3 | Complete   | 2026-03-23 | - |
| 8. Third-Party Provider Documentation | v1.2 | 0/TBD | Not started | - |
