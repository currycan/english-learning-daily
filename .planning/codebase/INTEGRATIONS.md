# External Integrations

**Analysis Date:** 2026-03-22

## APIs & External Services

**Push Notifications:**
- Bark (https://api.day.app) - iOS push notifications for daily learning tasks
  - SDK/Client: requests library (custom HTTP wrapper)
  - Auth: `BARK_TOKEN` environment variable (GitHub Secret)
  - Endpoint: `POST https://api.day.app/{token}`
  - Payload: JSON with `title`, `body`, optional `url`
  - Used by: `scripts/push_bark.py`

**Content Sources (Referenced, Not Integrated):**
- BBC - The English We Speak, BBC Worklife podcasts (user-referenced, not API integrated)
- Business English Pod - Podcast content (user-referenced)
- Harvard Business Review - Article sources (user-referenced)
- Reddit (r/jobs, r/cscareerquestions) - Article sources (user-referenced)
- Claude/ChatGPT - AI prompts for conversation practice (user-initiated, not API)

## Data Storage

**Local File Storage:**
- `plan/state.json` - Persistent user state (start date, completion log, scene ratings)
- `plan/config.json` - Non-sensitive configuration (push times, timezone)
- Both files use JSON format with UTF-8 encoding

**No Database:**
- All state persisted to JSON files in repository
- State managed via `scripts/plan_state.py` (load_state, save_state functions)

**File Storage:**
- Local filesystem only - no cloud storage integration

**Caching:**
- None - state loaded fresh on each script execution

## Authentication & Identity

**Auth Provider:**
- Custom (GitHub-based only)
  - Implementation: GitHub Actions secrets for `BARK_TOKEN`
  - No user authentication system (single-user CLI application)

**Secret Management:**
- GitHub Secrets: `BARK_TOKEN` stored as workflow secret
- Environment variables: populated by `.github/workflows/*.yml`
- Never stored in code or `plan/config.json`

## Monitoring & Observability

**Error Tracking:**
- None - workflow runs output to GitHub Actions logs

**Logs:**
- GitHub Actions job logs (stdout/stderr)
- No structured logging framework
- Scripts print status messages to stdout and errors to stderr

## CI/CD & Deployment

**Hosting:**
- GitHub Actions (Ubuntu-latest runners)

**CI Pipeline:**
- `.github/workflows/morning.yml` - Scheduled at 23:00 UTC (07:00 Asia/Shanghai)
  - Triggers: Cron schedule + manual workflow_dispatch
  - Steps: checkout → setup Python 3.12 → pip install → generate_task → push_bark
- `.github/workflows/evening.yml` - Scheduled at 13:00 UTC (21:00 Asia/Shanghai)
  - Triggers: Cron schedule + manual workflow_dispatch
  - Steps: checkout → setup Python 3.12 → pip install → check_evening → push_bark

**Deployment Trigger:**
- Scheduled cron jobs (no manual deployment required)
- Manual trigger via GitHub Actions UI (`workflow_dispatch`)

## Environment Configuration

**Required env vars:**
- `BARK_TOKEN` - Bark API authentication token (GitHub Secret, provided at workflow runtime)
- `PYTHONPATH` - Set to `.` in workflows to enable local module resolution

**Secrets location:**
- GitHub Secrets (accessed via `${{ secrets.BARK_TOKEN }}` in workflows)

**Configuration files:**
- `plan/config.json` - Push times (morning_hour, evening_hour) and timezone (Asia/Shanghai)
- `plan/state.json` - User state (no secrets, safe to commit)

## Webhooks & Callbacks

**Incoming:**
- None - application is event-driven (cron-triggered), no webhook endpoints

**Outgoing:**
- Bark API push: `POST https://api.day.app/{BARK_TOKEN}`
  - Triggered by `scripts/push_bark.py`
  - Payload: `{"title": str, "body": str, "url": str|null}`
- Git commits: `git add`, `git commit`, `git push` (local operations)
  - Triggered by `scripts/mark_done.py` when user marks blocks complete

## Data Flow

**Morning Workflow:**
1. GitHub Actions triggers at scheduled time
2. `scripts/generate_task.py` reads `plan/state.json`, generates task JSON
3. JSON piped to `scripts/push_bark.py`
4. `push_bark.py` sends HTTP POST to Bark API with title/body

**Evening Workflow:**
1. GitHub Actions triggers at scheduled time
2. `scripts/check_evening.py` reads `plan/state.json`, generates summary JSON
3. JSON piped to `scripts/push_bark.py`
4. `push_bark.py` sends HTTP POST to Bark API with completion status

**Manual Update Flow:**
1. User runs `python -m scripts.mark_done <block|rating> [value]`
2. `apply_command()` creates immutable copy of state via `copy.deepcopy()`
3. `save_state()` writes updated JSON to `plan/state.json`
4. `git_commit_and_push()` stages, commits, and pushes to remote

## Security Considerations

**Secrets:**
- `BARK_TOKEN` never logged or printed (only used in HTTP request)
- `push_bark.py` validates token presence before making request
- GitHub Secrets encryption ensures token not exposed in logs

**Input Validation:**
- `mark_done.py` validates command names against `VALID_BLOCKS`
- Rating values validated as integers 1-5
- JSON parsing wrapped in try/except with non-zero exit on error

**Error Handling:**
- All scripts exit with non-zero status on failure (required for GitHub Actions to mark job failed)
- HTTP errors from Bark API cause script failure with descriptive error message

---

*Integration audit: 2026-03-22*
