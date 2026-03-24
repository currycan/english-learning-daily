---
gsd_state_version: 1.0
milestone: v2.0
milestone_name: 学习网站
status: Defining requirements
stopped_at: —
last_updated: "2026-03-24T00:00:00.000Z"
progress:
  total_phases: 0
  completed_phases: 0
  total_plans: 0
  completed_plans: 0
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-03-24)

**Core value:** Every day a ready-to-read English lesson lands in git — real content with targeted vocabulary, chunking expressions, and exercises to deepen understanding.
**Current focus:** v2.0 学习网站 — defining requirements

## Current Position

Phase: Not started (defining requirements)
Plan: —
Status: Defining requirements
Last activity: 2026-03-24 — Milestone v2.0 学习网站 started

## Accumulated Context

### Decisions

All decisions logged in PROJECT.md Key Decisions table.

Key patterns carry forward:

- `set -eo pipefail` + three-stage pipe pattern for CI pipelines
- TDD RED → GREEN per plan, including documentation (write assertions first)
- Instantiate SDK clients inside functions for testability
- Bilingual (EN + ZH) docs format across all project docs
- [Phase 01]: Removed all Anthropic and OpenAI SDK code; single call_gemini() function with GEMINI_MODEL constant (gemini-2.5-flash-lite)

### Website Context

See: .planning/website-CONTEXT.md — full implementation decisions from discuss session.

Key decisions:
- Astro static site + GitHub Pages default domain
- Mobile-first, system dark/light auto-switch + manual toggle
- Collapsible sections (vocab/chunks/questions), answers hidden tap-to-reveal
- Calendar archive view, localStorage reading progress
- Build triggered by existing daily-content.yml workflow

### Roadmap Evolution

- v2.0 started: 学习网站 — Astro static site for reading daily lessons

### Pending Todos

None.

### Blockers/Concerns

None.

## Session Continuity

Last session: 2026-03-24
Stopped at: Milestone v2.0 started, requirements in progress
Resume file: None
