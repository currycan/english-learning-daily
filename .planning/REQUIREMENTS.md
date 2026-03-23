# Requirements: English Daily Content

**Defined:** 2026-03-23
**Core Value:** Every day a ready-to-read English lesson lands in git — real content with targeted vocabulary, chunking expressions, and exercises to deepen understanding.

## v1.2 Requirements

Requirements for third-party Claude-compatible API integration.

### Provider Extension

- [ ] **TPROV-01**: call_claude() uses custom base_url when configured (env var or config.json)
- [ ] **TPROV-02**: call_claude() uses custom auth_token when configured, independent of ANTHROPIC_API_KEY
- [ ] **TPROV-03**: When no custom base_url/auth_token configured, behavior is identical to v1.1 (backward compatible)
- [x] **TPROV-04**: Fallback chain works correctly when primary provider uses a third-party Claude endpoint

### Configuration

- [ ] **CONF-01**: ANTHROPIC_BASE_URL env var is read and applied at highest priority
- [ ] **CONF-02**: ANTHROPIC_AUTH_TOKEN env var is read and applied at highest priority
- [ ] **CONF-03**: plan/config.json supports anthropic_base_url and anthropic_auth_token fields (lower priority than env vars)
- [x] **CONF-04**: GitHub Actions workflow injects ANTHROPIC_BASE_URL and ANTHROPIC_AUTH_TOKEN from repository secrets

### Documentation

- [ ] **DOCS-01**: docs/ai-providers.md includes third-party provider setup section (bilingual Chinese/English format)
- [ ] **DOCS-02**: docs/ai-providers.md config.json example shows anthropic_base_url and anthropic_auth_token fields
- [ ] **DOCS-03**: docs/ai-providers.md GitHub Secrets section explains adding custom base_url and token as secrets

### Tests

- [ ] **TEST-01**: Unit tests verify custom base_url and auth_token are passed to anthropic.Anthropic() client
- [ ] **TEST-02**: Unit test confirms backward compatibility — missing config falls back to standard Anthropic behavior

## Future Requirements

### Provider Extension

- **TPROV-05**: Support multiple named third-party profiles (e.g., switch between orcai / openrouter by name)

## Out of Scope

| Feature | Reason |
|---------|--------|
| Load balancing across third-party providers | Overkill for one call/day; fallback is sufficient |
| Auto-discovery of third-party endpoints | Manual config is explicit and secure |
| Third-party OpenAI-compatible proxy support | OpenAI SDK already handles this; separate concern |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| TPROV-01 | Phase 7 | Pending |
| TPROV-02 | Phase 7 | Pending |
| TPROV-03 | Phase 7 | Pending |
| TPROV-04 | Phase 7 | Complete |
| CONF-01 | Phase 7 | Pending |
| CONF-02 | Phase 7 | Pending |
| CONF-03 | Phase 7 | Pending |
| CONF-04 | Phase 7 | Complete |
| TEST-01 | Phase 7 | Pending |
| TEST-02 | Phase 7 | Pending |
| DOCS-01 | Phase 8 | Pending |
| DOCS-02 | Phase 8 | Pending |
| DOCS-03 | Phase 8 | Pending |

**Coverage:**
- v1.2 requirements: 13 total
- Mapped to phases: 13
- Unmapped: 0 ✓

---
*Requirements defined: 2026-03-23*
*Last updated: 2026-03-23 after roadmap creation*
