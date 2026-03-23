# Phase 4: Provider Abstraction + OpenAI Integration - Context

**Gathered:** 2026-03-23
**Status:** Ready for planning

<domain>
## Phase Boundary

Decouple AI provider from content generation logic so the system can call either Claude (anthropic) or OpenAI (gpt-4o-mini) via a unified interface, selected by env var or config.json. Fallback behavior is Phase 5. Documentation is Phase 6.

</domain>

<decisions>
## Implementation Decisions

### Prompt Strategy
- Single shared prompt for both providers — same `build_prompt()` output sent to whichever provider is active
- No provider-specific prompt tuning; output format consistency guaranteed by prompt rules, not by tailoring

### Config Schema
- Add two top-level fields to `plan/config.json`:
  - `"ai_provider": "anthropic"` — default provider; overridden by `AI_PROVIDER` env var at runtime
  - `"openai_model": "gpt-4o-mini"` — OpenAI model; configurable, defaults to gpt-4o-mini
- Claude model (`claude-haiku-4-5-20251001`) stays hardcoded in source — not moved to config
- New config fields sit at the same level as `content_feeds`, `timezone`

### Provider Resolution
- Priority: `AI_PROVIDER` env var (if set and non-empty) overrides `ai_provider` from config.json
- Resolution happens once at script entry, passed into the generation function

### Error Handling for Invalid Provider
- If `AI_PROVIDER` or `ai_provider` config resolves to an unknown value (not `"anthropic"` or `"openai"`): `sys.exit(1)` with a clear stderr message listing valid values
- No silent defaulting — misconfiguration must be visible

### OpenAI Client Pattern
- `openai.OpenAI()` instantiated inside the call function (same pattern as `anthropic.Anthropic()` inside `call_claude()`) — keeps patching clean in tests
- Response extraction: `response.choices[0].message.content`

### CI Workflow Changes
- `daily-content.yml` env block: add `OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}` alongside existing `ANTHROPIC_API_KEY`
- `AI_PROVIDER` is NOT added to yml env — provider selection is controlled via `plan/config.json`, no yml changes needed when switching
- Missing/unused API key (e.g., OPENAI_API_KEY is empty when provider=anthropic) is fine — only the active provider's key is used

### Module Structure
- New file `scripts/ai_provider.py` encapsulates provider selection, both `call_claude()` and `call_openai()`, and a unified `call_ai(prompt, provider, model_config)` dispatcher
- `generate_exercises.py` imports from `ai_provider.py` instead of calling `anthropic` directly
- `build_prompt()`, `parse_response()`, `render_markdown()` stay in `generate_exercises.py` unchanged

### Claude's Discretion
- Exact function signatures inside `ai_provider.py`
- How `model_config` is passed (dict slice vs individual args)
- Whether to use a single `call_ai()` or keep `call_claude()` / `call_openai()` as named functions dispatched by a wrapper

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements
- `.planning/REQUIREMENTS.md` — PRVD-01, PRVD-02, PRVD-03, OAPI-01, OAPI-02, OAPI-03, TEST-01

### Existing Implementation
- `scripts/generate_exercises.py` — current Claude-only implementation; `call_claude()` and `MODEL` are the only provider-specific parts; `build_prompt()`, `parse_response()`, `render_markdown()` are provider-agnostic and must not change
- `plan/config.json` — existing config schema; new fields are added at top level
- `.github/workflows/daily-content.yml` — CI pipeline; needs `OPENAI_API_KEY` added to env block

### Codebase Conventions
- `.planning/codebase/CONVENTIONS.md` — naming, error handling, immutability patterns
- `.planning/codebase/ARCHITECTURE.md` — layer structure, data flow, entry points

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `generate_exercises.py:build_prompt()` — provider-agnostic, returns prompt string; reuse as-is
- `generate_exercises.py:parse_response()` — provider-agnostic JSON validator; reuse as-is
- `generate_exercises.py:render_markdown()` — provider-agnostic renderer; reuse as-is
- `generate_exercises.py:call_claude()` — provider-specific; refactor into `ai_provider.py`

### Established Patterns
- `anthropic.Anthropic()` instantiated inside `call_claude()` — same pattern for `openai.OpenAI()` in new code
- `sys.exit(1)` + stderr message on API errors — same pattern for OpenAI errors
- Constants in UPPER_CASE at module level (`MODEL`) — apply to new provider constants
- Type hints on all function signatures

### Integration Points
- `generate_exercises.py:main()` calls `call_claude()` directly — change to `call_ai()` from `ai_provider.py`
- `plan/config.json` loaded in other scripts (e.g., `feed_article.py`) — verify `ai_provider` loading doesn't break existing loaders
- `requirements.txt` — add `openai` SDK

</code_context>

<specifics>
## Specific Ideas

No specific requirements — open to standard approaches for the `ai_provider.py` structure.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 04-provider-abstraction-openai-integration*
*Context gathered: 2026-03-23*
