# Codebase Concerns

**Analysis Date:** 2026-03-22

## Tech Debt

**Unused Configuration File:**
- Issue: `plan/config.json` exists and is documented in README but is never read or used by any script
- Files: `plan/config.json` is defined but not imported or referenced in `scripts/plan_state.py`, `scripts/generate_task.py`, `scripts/check_evening.py`, or any other script
- Impact: Misleading documentation; developers may expect timezone-aware time calculations but they don't happen; hardcoded UTC times in workflows cannot be customized
- Fix approach: Either remove config.json and document hardcoded schedule in README, or implement config loading in `scripts/plan_state.py` to read and apply timezone conversions

**Hardcoded Times in Workflow Files:**
- Issue: Cron schedules in `.github/workflows/morning.yml` and `.github/workflows/evening.yml` are hardcoded to UTC times (23:00 UTC for 07:00 BJT, 13:00 UTC for 21:00 BJT)
- Files: `.github/workflows/morning.yml` (line 5), `.github/workflows/evening.yml` (line 5)
- Impact: Cannot be easily adjusted for different timezones without modifying workflow files; users must commit timezone changes
- Fix approach: Use GitHub Actions workflow environment variables or reference config.json if timezone support is needed

**Scene Roadmap Hardcoded in Code:**
- Issue: `SCENE_ROADMAP` is a 160+ line hardcoded constant in `scripts/plan_state.py` that defines all scenes, podcasts, articles, and AI prompts
- Files: `scripts/plan_state.py` (lines 7-106)
- Impact: Any scene content updates require code changes; no way for users to customize scenes or prompts without modifying Python; scenes cannot be adapted to different languages or learning styles
- Fix approach: Move `SCENE_ROADMAP` to a JSON or YAML file (e.g., `plan/scenes.json`) and load it at runtime; this enables non-technical users to customize content

**No Explicit Validation of State Schema:**
- Issue: Functions assume state dict has required keys (`start_date`, `scene_ratings`, `daily_log`) but do not validate structure
- Files: `scripts/plan_state.py`, `scripts/generate_task.py` (line 18), `scripts/check_evening.py` (line 21), `scripts/mark_done.py` (lines 21-54)
- Impact: If `state.json` is corrupted or missing a key, scripts fail with cryptic KeyError or AttributeError instead of clear error messages; state corruption is not caught early
- Fix approach: Add a `validate_state(state: dict) -> bool` function that checks required keys exist and have correct types, call it in `load_state()` before returning

## Known Bugs

**Edge Case: Pre-Start-Date Check Fails for Single-Day Future Dates:**
- Symptoms: When run before `start_date`, the message uses "tomorrow" label only when `days_until == 1`, but the calculation `(start - today).days` may be off by one due to date boundary issues
- Files: `scripts/generate_task.py` (lines 21-28), `scripts/check_evening.py` (lines 24-31)
- Trigger: Run on the day before start_date (e.g., start_date = 2026-03-21, run on 2026-03-20)
- Workaround: Users should not trigger workflows before start_date; the scheduled workflows won't run until after the schedule begins
- Note: Tests exist (`test_generate_task.py` and `test_check_evening.py`) but do not cover pre-start-date scenarios explicitly

**Evening Payload Fallback Logic for Legacy daily_log Entries:**
- Symptoms: If `daily_log` contains entries but not one matching today's ISO date string, code falls back to first entry in dict (`next(iter(daily_log_dict.values()))`)
- Files: `scripts/check_evening.py` (lines 44-45)
- Impact: In scenarios where daily_log is manually edited or migrated, fallback picks an arbitrary entry instead of safely assuming an empty day, leading to incorrect completion percentages
- Trigger: Manual editing of state.json or migration from older versions with different date key format
- Workaround: Always ensure today's date has an entry in daily_log
- Note: Test exists (`test_check_evening.py` line 24+) but only tests the normal case; no test covers the fallback path

## Security Considerations

**No Validation of Bark API Response:**
- Risk: If Bark API is compromised or returns unexpected JSON, `send_to_bark()` only checks HTTP status code, not response format
- Files: `scripts/push_bark.py` (lines 24-28)
- Current mitigation: Bark API is a trusted third-party service; status code check is present
- Recommendations: Log response body for debugging; consider parsing JSON response to verify success field if API schema changes

**Bark Token Exposure in Git History:**
- Risk: If BARK_TOKEN is accidentally committed to git (via state.json or environment leakage), it exists in history and can be leaked
- Files: All scripts that use `BARK_TOKEN` env var; `.github/workflows/morning.yml`, `.github/workflows/evening.yml`
- Current mitigation: `.gitignore` should exclude `.env` files; GitHub Secrets are not logged; code uses `os.environ.get()` safely
- Recommendations: Add `.env` and `.env.local` to `.gitignore` if users test locally; consider commit hooks to prevent secrets in commits; audit git log for accidental token commits

**No Rate Limiting on Bark API Calls:**
- Risk: If workflows trigger rapidly (e.g., manual retriggers), could exceed Bark API rate limits or be flagged as abuse
- Files: `scripts/push_bark.py` (line 24), `.github/workflows/morning.yml`, `.github/workflows/evening.yml`
- Current mitigation: Workflows are scheduled to run exactly twice per day; manual runs are developer-controlled
- Recommendations: Add delays between retries; implement exponential backoff if Bark returns rate-limit status; log API call timestamps

## Performance Bottlenecks

**No Caching of Scene Lookups:**
- Problem: `get_scene_for_week()` iterates through `SCENE_ROADMAP` on every call; with 112+ days per plan, this happens repeatedly
- Files: `scripts/plan_state.py` (lines 129-144), called from `scripts/generate_task.py`, `scripts/check_evening.py`, `scripts/mark_done.py`
- Cause: Roadmap is a list, lookups are O(n) instead of O(1); not cached between script invocations
- Improvement path: Pre-index SCENE_ROADMAP as a dict keyed by week number at module load; for weeks 15+, compute once and store in state.json to avoid recalculation

**No Batch Operations for Git Commits:**
- Problem: `mark_done.py` calls `git add`, `git commit`, `git push` as three separate subprocess calls
- Files: `scripts/mark_done.py` (lines 57-64)
- Cause: Three individual network round-trips instead of one atomic push; increases latency and risk of partial state
- Improvement path: Combine into single `git push` after adding and committing; or use GitHub API to update state.json directly

## Fragile Areas

**Temporal Calculations Depend Entirely on `start_date`:**
- Files: `scripts/plan_state.py` (lines 109-127), all payload-building functions
- Why fragile: If `start_date` is invalid (e.g., "2026-99-99"), parsing fails with unclear error; no validation that start_date is in correct ISO format
- Safe modification: Always validate `start_date` against `date.fromisoformat()` in a try-except; add test for invalid date formats; store as date object in state if schema allows
- Test coverage: `test_plan_state.py` only tests valid dates; no tests for malformed `start_date` string

**Daily Log Entry Creation is Scattered:**
- Files: `scripts/mark_done.py` (lines 30-31) creates entry if missing; `scripts/check_evening.py` (lines 47-48) also creates entry if missing
- Why fragile: Two different code paths initialize the same structure; if one is updated and the other isn't, schema divergence occurs
- Safe modification: Create a utility function `ensure_daily_log_entry(state: dict, date_str: str) -> None` in `plan_state.py` and call it from both locations
- Test coverage: Tests for mark_done exist; tests for check_evening don't explicitly cover missing entry creation

**No Idempotency Guarantee for mark_done Commands:**
- Files: `scripts/mark_done.py` (lines 35-38 for "all", lines 39-40 for "skip", lines 41-49 for ratings)
- Why fragile: Calling `mark_done.py review` twice creates a git commit each time, even if the state didn't change; `git_commit_and_push()` will fail on second call if no changes exist
- Safe modification: Check if state changed before committing; only commit if `new_state != state`; or catch git commit error for "nothing to commit" case
- Test coverage: `test_mark_done.py` line 28-32 tests duplicate block prevention in state, but not the git operation side effects

## Scaling Limits

**State File Size Growth Over Time:**
- Current capacity: `daily_log` grows by 1 entry per day, 112 days over 16 weeks = ~112 JSON objects
- Limit: At 100 bytes per entry, ~11 KB per completion cycle; not a concern for storage, but git history compounds with every `mark_done.py` push
- Scaling path: Archive old daily_log entries (e.g., summarize weekly into a single entry after week is complete); keep only current + recent weeks in state.json

**No Pagination for Multi-Cycle Users:**
- Current capacity: Plan is designed for exactly one 16-week cycle; supports weeks 15-16 auto-selection but not multiple cycles
- Limit: If users repeat the program, state.json has no mechanism to track multiple cycles or reset scene_ratings between cycles
- Scaling path: Add `"cycles": [{ "start_date": "...", "scene_ratings": {...}, "daily_log": {...} }]` structure to support multiple runs

## Dependencies at Risk

**Requests Library Timeout Hard-Coded:**
- Risk: `scripts/push_bark.py` line 24 uses `timeout=10` with no configuration option; if Bark API is slow, requests will always timeout
- Impact: Workflow fails silently if Bark API latency exceeds 10 seconds
- Migration plan: Make timeout configurable via environment variable or config.json; log warnings if requests approach timeout

**No Fallback Push Mechanism:**
- Risk: If Bark API is down, workflows fail with no alternative notification mechanism
- Impact: Users don't receive learning reminders; no notification of failure
- Scaling path: Add fallback to email or webhook on Bark failure; or store pending notifications in state.json and retry on next run

## Missing Critical Features

**No Manual Workflow Trigger Safeguards:**
- Problem: GitHub Actions allow manual trigger of workflows (workflow_dispatch), but there's no rate limiting or confirmation
- Blocks: Users can accidentally spam themselves with push notifications by clicking "Run workflow" repeatedly
- Recommendation: Add a check in `main()` to skip if a push was sent in the last hour; or add GitHub environment protection rules

**No Offline Mode:**
- Problem: All scripts require network access to push notifications; running locally without GitHub Actions requires manual Bark token setup
- Blocks: Developers cannot test full workflow locally without exposing Bark token in command line
- Recommendation: Add `--dry-run` flag to generate_task.py and check_evening.py to print payload without calling push_bark.py

**No Undo/Correction Mechanism:**
- Problem: Once `mark_done.py` commits state.json, there's no easy way to undo if the user made a mistake
- Blocks: Users cannot mark a block as incomplete if they realized they didn't actually finish it
- Recommendation: Add `mark_done.py undo <block>` command or `mark_done.py correct <block> <new_value>` to allow corrections

## Test Coverage Gaps

**No Tests for Pre-Start-Date Scenarios:**
- What's not tested: Calling `build_morning_payload()` or `build_evening_payload()` when `today < start_date`
- Files: `scripts/generate_task.py`, `scripts/check_evening.py` (lines 21-28)
- Risk: Edge case where workflows run before user sets start_date could silently produce incorrect payloads
- Priority: Medium — happens only if workflows are triggered manually before start_date

**No Tests for Malformed State.json:**
- What's not tested: Loading state.json with missing keys, wrong types (e.g., `start_date` as array), or invalid dates
- Files: `scripts/plan_state.py` (lines 147-152)
- Risk: Cryptic errors instead of user-friendly messages; developers have to debug JSON parsing errors
- Priority: High — corrupted state.json would break the entire system

**No Tests for Git Command Failures:**
- What's not tested: `mark_done.py` behavior when git commands fail (no remote, permission denied, merge conflict)
- Files: `scripts/mark_done.py` (lines 57-64)
- Risk: State is updated locally but push fails, leaving user's local repo out of sync with GitHub
- Priority: High — could cause data loss or merge conflicts

**No Integration Tests for Workflow Execution:**
- What's not tested: End-to-end workflow in GitHub Actions environment (PYTHONPATH, environment variables, secret access)
- Files: `.github/workflows/morning.yml`, `.github/workflows/evening.yml`
- Risk: Workflows could fail in CI even if local tests pass due to path or environment issues
- Priority: Medium — previous commits show this was an issue (see "fix: add PYTHONPATH=. to workflows for module resolution")

**No Tests for Scene Ratings Edge Cases:**
- What's not tested: Weeks 15-16 behavior with empty ratings dict, missing scene names, or mismatched scene names in roadmap vs. ratings
- Files: `scripts/plan_state.py` (lines 136-144)
- Risk: If scene name in roadmap is updated but ratings dict still has old name, the selection logic could break
- Priority: Low — happens only if roadmap is edited manually

---

*Concerns audit: 2026-03-22*
