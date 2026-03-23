---
gsd_state_version: 1.0
milestone: v1.1
milestone_name: Dual AI Provider
status: planning
stopped_at: Completed 04-02-PLAN.md
last_updated: "2026-03-23T04:00:00.000Z"
last_activity: 2026-03-23 — Phase 4 complete: provider abstraction wired end-to-end
progress:
  total_phases: 3
  completed_phases: 0
  total_plans: 2
  completed_plans: 2
  percent: 50
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-03-23)

**Core value:** Every day a ready-to-read English lesson lands in git — real content with targeted vocabulary, chunking expressions, and exercises to deepen understanding.
**Current focus:** Phase 4 — Provider Abstraction + OpenAI Integration

## Current Position

Phase: 4 of 6 (Provider Abstraction + OpenAI Integration)
Plan: 2 of 2 in current phase (COMPLETE)
Status: Phase 4 complete — ready for Phase 5
Last activity: 2026-03-23 — Phase 4 plans 01 and 02 complete

Progress: [█████░░░░░] 50% (v1.0 complete, Phase 4 complete)

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

### Pending Todos

None.

### Decisions Added (Phase 04-02)

- Provider selection controlled via plan/config.json not CI env var (AI_PROVIDER not added to yml)
- _load_config() uses Path(__file__).parent.parent / "plan" / "config.json" for CWD-independent resolution
- model_config dict with openai_model key passed to call_ai for OpenAI routing

### Blockers/Concerns

- [Human Verification Needed] Confirm OPENAI_API_KEY secret available in GitHub repo before CI runs (OPENAI_API_KEY now in workflow; secret must be added manually in GitHub Settings)
- [Note] OAPI-03 grep audit hits false positive in ai_provider.py comment line — no actual key in source

## Session Continuity

Last session: 2026-03-23T04:00:00.000Z
Stopped at: Completed 04-02-PLAN.md
Resume file: None
