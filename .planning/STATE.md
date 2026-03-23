---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
status: Not started
stopped_at: Completed 07-02-PLAN.md
last_updated: "2026-03-23T06:26:46.112Z"
last_activity: 2026-03-23 — Roadmap created for v1.2
progress:
  total_phases: 2
  completed_phases: 1
  total_plans: 3
  completed_plans: 3
  percent: 75
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-03-23)

**Core value:** Every day a ready-to-read English lesson lands in git — real content with targeted vocabulary, chunking expressions, and exercises to deepen understanding.
**Current focus:** Phase 7 — Custom Endpoint Implementation (v1.2)

## Current Position

Phase: 7 — Custom Endpoint Implementation
Plan: —
Status: Not started
Last activity: 2026-03-23 — Roadmap created for v1.2

Progress: [████████░░] 75% (v1.0 phases 1-3 complete, v1.1 phases 4-6 complete)

## Accumulated Context

### Decisions

All v1.0 decisions logged in PROJECT.md Key Decisions table.

Key technical decisions carry forward:
- newsinlevels.com/feed as primary RSS (only verified URL returning 800+ char bodies)
- claude-3-5-haiku-20241022 pinned exact — ~1,400 tokens/day
- anthropic.Anthropic() instantiated inside call_claude() for testability — same pattern for OpenAI client
- set -eo pipefail ensures CI failure propagation through three-stage pipe

v1.1 decisions:
- TEST-01 and TEST-02 embedded in implementation phases (4 and 5), not isolated
- Fallback ordering: configured provider first → other provider (symmetric)
- [Phase 04]: call_claude catches anthropic.APIError specifically (not bare Exception) — fixes v1.0 tech debt
- [Phase 04]: openai.OpenAI() inside call_openai() for testability, mirrors anthropic pattern
- [Phase 04]: CLAUDE_MODEL hardcoded in ai_provider.py as CLAUDE_MODEL constant, not in config
- [Phase 06]: Module-scoped pytest fixture raises FileNotFoundError (not silent skip) for clear TDD RED state
- [Phase 06]: Bilingual doc format (English + Chinese) matches existing docs/setup-guide.md style
- [Phase 06-02]: OPENAI_API_KEY inserted as third row in GitHub Secrets table after ANTHROPIC_API_KEY; Step 7a added in setup-guide.md with cross-link to ai-providers.md

v1.2 decisions:
- TPROV and CONF requirements merged into Phase 7 (tightly coupled: config layer feeds directly into client constructor)
- TEST-01 and TEST-02 embedded in Phase 7 per TDD practice established in v1.1
- DOCS requirements isolated in Phase 8 (depends on Phase 7 implementation being stable)
- Priority order: env vars (ANTHROPIC_BASE_URL, ANTHROPIC_AUTH_TOKEN) > config.json fields > SDK defaults
- [Phase 07-custom-endpoint-implementation]: New env vars placed in step-level env block only, not top-level — secrets are scoped to the generate step
- [Phase 07-custom-endpoint-implementation]: No conditional YAML logic — GitHub returns empty string for missing secrets, call_claude() treats as absent
- [Phase 07-custom-endpoint-implementation]: Backward compat test passes immediately — Anthropic() with no args already matches no-env-var contract; RED state confirmed by other 2 tests failing
- [Phase 07-custom-endpoint-implementation]: Test 3 uses base_url kwarg directly on call_claude() to represent config.json path (CONF-03); requires Plan 02 to add base_url parameter
- [Phase 07-custom-endpoint-implementation]: Conditional kwargs dict pattern — kwargs[key] set only when non-empty; avoids overriding SDK defaults with None or empty string
- [Phase 07-custom-endpoint-implementation]: os.environ.get() or kwarg or '' chain handles GitHub Actions empty-string secret behavior for ANTHROPIC_BASE_URL and ANTHROPIC_AUTH_TOKEN

### Decisions Added (Phase 04-02)

- Provider selection controlled via plan/config.json not CI env var (AI_PROVIDER not added to yml)
- _load_config() uses Path(__file__).parent.parent / "plan" / "config.json" for CWD-independent resolution
- model_config dict with openai_model key passed to call_ai for OpenAI routing

### Decisions Added (Phase 05-01)

- ProviderError raised from call_claude/call_openai instead of sys.exit(1) — keeps low-level callers composable
- _backup_provider uses set difference on VALID_PROVIDERS — deterministic with exactly two providers
- _dispatch private helper avoids code duplication between primary and fallback paths in call_ai
- bare Exception in call_openai is correct (wider net, consistent with Phase 4 decision; openai.OpenAIError not used)
- generate_exercises.py unchanged — call_ai() interface fully backward-compatible

### Pending Todos

None.

### Blockers/Concerns

- [Human Verification Needed] Confirm OPENAI_API_KEY secret available in GitHub repo before CI runs (OPENAI_API_KEY now in workflow; secret must be added manually in GitHub Settings)
- [Note] OAPI-03 grep audit hits false positive in ai_provider.py comment line — no actual key in source

## Session Continuity

Last session: 2026-03-23T06:24:09.516Z
Stopped at: Completed 07-02-PLAN.md
Resume file: None
