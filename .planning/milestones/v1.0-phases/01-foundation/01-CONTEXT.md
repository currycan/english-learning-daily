# Phase 1: Foundation - Context

**Gathered:** 2026-03-22
**Status:** Ready for planning

<domain>
## Phase Boundary

CI infrastructure for the daily content pipeline: a GitHub Actions workflow that runs daily, commits a file to `content/YYYY-MM-DD.md` using Beijing time, has write permissions, gracefully skips if today's file already exists, and fails loudly on errors. No RSS fetching or AI generation yet — just the skeleton and shared utilities.

</domain>

<decisions>
## Implementation Decisions

### Cron Schedule
- Run at `0 22 * * *` UTC (= 06:00 BJT next day)
- Content must be available before 08:30 BJT on weekdays (user's morning study time)
- 06:00 BJT gives a comfortable 2.5-hour buffer before reading time
- Same cron expression for every day (weekday and weekend)

### Re-run / Idempotency
- If `content/YYYY-MM-DD.md` already exists when the workflow runs, skip all processing and exit 0 cleanly
- No overwrite on re-run — content is stable once committed for the day
- This saves API calls and prevents content churn when debugging with `workflow_dispatch`

### content/ Directory
- Scripts create `content/` directory automatically with `mkdir -p` if it doesn't exist
- No pre-committed placeholder file or README needed — first real run creates the directory
- `pathlib.Path("content").mkdir(parents=True, exist_ok=True)` — follows existing pattern

### Workflow Structure
- New workflow file: `.github/workflows/daily-content.yml`
- Follows exact same structure as existing `morning.yml` (checkout → setup-python → pip install → run script)
- Adds `permissions: contents: write` at the job level (missing from existing workflows — must add explicitly)
- Adds git identity config step before commit: `git config user.name "github-actions[bot]"` and `git config user.email "github-actions[bot]@users.noreply.github.com"`
- Uses `GITHUB_TOKEN` (built-in) for push — no PAT needed

### Failure Handling
- Pipeline exits non-zero (`sys.exit(1)`) on any failure — matches existing codebase convention
- Error messages to stderr — matches existing `print(f"ERROR: ...", file=sys.stderr)` pattern
- CI job marked failed in GitHub Actions when exit code is non-zero

### Shared Utilities Module
- Create `scripts/content_utils.py` for date derivation and shared helpers
- Key function: `get_beijing_date() -> date` — returns today's date in CST (UTC+8) regardless of runner timezone
- Key function: `content_path(date: date) -> Path` — returns `Path(f"content/{date.isoformat()}.md")`
- Follows existing pattern from `scripts/plan_state.py`: pure functions, type hints, no side effects

### Claude's Discretion
- Exact git commit message format for the daily content commit
- Whether to use a `dry_run` flag in Phase 1 placeholder script for testing
- Exact CI step names and comments in the workflow YAML

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Existing CI Patterns
- `.github/workflows/morning.yml` — Existing workflow structure to mirror (cron, steps, env vars)
- `.github/workflows/evening.yml` — Second workflow for reference

### Project Constraints
- `.planning/PROJECT.md` — Tech stack constraints (Python only, no new deps beyond requests + anthropic)
- `.planning/REQUIREMENTS.md` §CI Workflow — CI-01 and CI-02 acceptance criteria

### Codebase Conventions
- `.planning/codebase/CONVENTIONS.md` — Snake_case, sys.exit(1) pattern, stderr for errors, immutability
- `.planning/codebase/ARCHITECTURE.md` — Pipeline architecture, script responsibilities

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `scripts/plan_state.py`: Pattern for `get_beijing_date()` — similar timezone-aware date logic can be adapted (existing code uses `date.today()` without explicit timezone; new utility must use `datetime.now(tz=timezone(timedelta(hours=8))).date()`)
- `scripts/mark_done.py`: `git_commit_and_push()` function — exact pattern to reuse for committing content files from CI

### Established Patterns
- `sys.exit(1)` on all errors: every script in the codebase follows this — mandatory
- `print(..., file=sys.stderr)` for errors, `print(...)` for status: established logging convention
- Pure functions with type hints: `def func(param: type) -> return_type:` — follow throughout
- `from pathlib import Path` for all file I/O — already the standard
- `main()` entry point: all executable scripts have a `main()` function called at `if __name__ == "__main__"`

### Integration Points
- New workflow `daily-content.yml` runs independently of existing `morning.yml` / `evening.yml`
- `scripts/content_utils.py` will be imported by `fetch_article.py`, `generate_exercises.py`, `render_markdown.py`, `commit_content.py` in later phases
- `content/` directory is new — no conflict with existing `plan/` directory

</code_context>

<specifics>
## Specific Ideas

- User reads in the morning (08:30 weekdays, 09:30 weekends) and evening (22:00 weekdays, 23:00 weekends)
- Content uses the SAME article for both morning and evening sessions — morning: article + vocabulary; evening: chunking + comprehension questions
- The Markdown file structure should support a natural morning/evening split (captured as Phase 3 input)
- Cron fires at 22:00 UTC (= 06:00 BJT) to ensure content is available well before 08:30 reading time

</specifics>

<deferred>
## Deferred Ideas

- Morning/evening file structure split for AM/PM study sessions — Phase 3 (Markdown rendering)
- Push notification linking to today's content file — out of scope (user reads git directly)
- Weekend cron override (one hour later) — not implemented; GitHub Actions cron doesn't support conditional schedules; single cron at 22:00 UTC serves all days

</deferred>

---

*Phase: 01-foundation*
*Context gathered: 2026-03-22*
