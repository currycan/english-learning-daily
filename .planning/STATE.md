---
gsd_state_version: 1.0
milestone: v1.2
milestone_name: Third-Party Claude API
status: defining_requirements
stopped_at: —
last_updated: "2026-03-23T00:00:00.000Z"
last_activity: 2026-03-23 — Milestone v1.2 started
progress:
  total_phases: 0
  completed_phases: 0
  total_plans: 0
  completed_plans: 0
  percent: 0
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-03-23)

**Core value:** Every day a ready-to-read English lesson lands in git — real content with targeted vocabulary, chunking expressions, and exercises to deepen understanding.
**Current focus:** Defining requirements for v1.2

## Current Position

Phase: Not started (defining requirements)
Plan: —
Status: Defining requirements
Last activity: 2026-03-23 — Milestone v1.2 started

Progress: [███████░░░] 75% (v1.0 complete, Phase 4 complete, Phase 5 complete)

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
- [Phase 04]: openai.OpenAI() instantiated inside call_openai() for testability, mirrors anthropic pattern
- [Phase 04]: CLAUDE_MODEL hardcoded in ai_provider.py as CLAUDE_MODEL constant, not in config
- [Phase 06]: Module-scoped pytest fixture raises FileNotFoundError (not silent skip) for clear TDD RED state
- [Phase 06]: Bilingual doc format (English + Chinese) matches existing docs/setup-guide.md style
- [Phase 06-02]: OPENAI_API_KEY inserted as third row in GitHub Secrets table after ANTHROPIC_API_KEY; Step 7a added in setup-guide.md with cross-link to ai-providers.md

### Pending Todos

None.

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

### Blockers/Concerns

- [Human Verification Needed] Confirm OPENAI_API_KEY secret available in GitHub repo before CI runs (OPENAI_API_KEY now in workflow; secret must be added manually in GitHub Settings)
- [Note] OAPI-03 grep audit hits false positive in ai_provider.py comment line — no actual key in source

## Session Continuity

Last session: 2026-03-23T05:37:06.152Z
Stopped at: Completed 06-02-PLAN.md
Resume file: None
