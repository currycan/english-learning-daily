# English Learning Daily — Claude Code Configuration

## Project Overview

Automated English learning task pusher. GitHub Actions triggers twice daily, reads `plan/state.json`, generates task content, and sends push notifications to iPhone via Bark.

## Key Files

| File | Responsibility |
|------|---------------|
| `plan/state.json` | Source of truth: start date, daily completion log, scene ratings |
| `plan/config.json` | Push times and timezone (no secrets here) |
| `scripts/plan_state.py` | All temporal calculations + state I/O |
| `scripts/generate_task.py` | Morning push payload builder |
| `scripts/check_evening.py` | Evening push payload builder |
| `scripts/push_bark.py` | Bark API client — reads JSON from stdin |

## Architecture

Scripts communicate via stdout → stdin JSON pipe:

```
generate_task.py  ──stdout──▶  push_bark.py
check_evening.py  ──stdout──▶  push_bark.py
```

JSON envelope: `{"title": str, "body": str, "url": str | null}`

All temporal values (`current_week`, `plan_day`, `scene_cycle_day`, etc.) are derived from `start_date` at runtime — never stored in `state.json`.

## Running Tests

```bash
pytest                          # all tests
pytest tests/test_plan_state.py # specific file
pytest -v                       # verbose
```

## Running Scripts Locally

Always run from the project root using `-m` (so `scripts/` is importable):

```bash
python -m scripts.generate_task          # preview morning payload
python -m scripts.check_evening          # preview evening payload
```

## Critical Constraints

- **Immutability**: `state.json` mutations must use `copy.deepcopy`.
- **No secrets in code**: `BARK_TOKEN` comes from environment only. Never commit it.
- **Derived state**: Do not add computed fields to `state.json`. Compute from `start_date` every time.
- **Exit non-zero on failure**: All scripts must `sys.exit(1)` on error so GitHub Actions marks the job failed.

## State Schema

```json
{
  "start_date": "YYYY-MM-DD",
  "scene_ratings": { "Scene name": 1-5 },
  "daily_log": {
    "YYYY-MM-DD": { "completed": ["review", "input"], "skipped": false }
  }
}
```

Valid block names: `review`, `input`, `extraction`, `output`

## Scene Roadmap

Weeks 1–14 map to 7 scenes (2 weeks each). Weeks 15–16 auto-select the lowest-rated scene from `scene_ratings`. Scene names must match exactly as defined in `SCENE_ROADMAP` in `plan_state.py`.
