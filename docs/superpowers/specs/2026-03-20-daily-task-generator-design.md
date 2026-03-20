# Daily Task Generator — Design Spec

**Date:** 2026-03-20
**Author:** Andrew
**Goal:** Automatically generate and push daily English learning tasks to iPhone via Bark, based on the English learning plan spec

---

## Background

The English learning plan (`2026-03-20-english-learning-design.md`) defines a 16-week, scene-driven study structure with four daily blocks (Review, Input, Extraction, Output). This system automates daily task generation and delivery so the learner does not need to manually look up what to do each day.

**Delivery requirements:**
- Platform: Bark (iOS push notification app)
- Frequency: Morning push (07:00 BJT) + Evening push (21:00 BJT)
- Content: Detailed guidance per block including podcast recommendations and AI prompts
- Tracking: Full completion tracking with biweekly scene-rating reminders

---

## Architecture

```
GitHub Repo
├── plan/
│   ├── state.json          # Current progress and completion log
│   └── config.json         # Push times, plan start date, timezone
├── scripts/
│   ├── generate_task.py    # Generate today's task content
│   ├── push_bark.py        # Call Bark API to send notification
│   ├── mark_done.py        # Mark blocks complete, commit and push state
│   └── check_evening.py    # Compute completion rate, generate evening push
└── .github/workflows/
    ├── morning.yml         # Scheduled morning trigger
    └── evening.yml         # Scheduled evening trigger
```

**Data flow:**

1. GitHub Actions triggers on schedule → runs scripts → reads `state.json` → generates task content → calls Bark API → notification appears on phone
2. Learner completes a block → runs `python scripts/mark_done.py <block>` locally → script commits and pushes updated `state.json`
3. Evening Actions trigger → reads today's completion data → pushes summary + tomorrow preview
4. Every 14th day of a scene cycle → evening push appends biweekly rating reminder

---

## Data Model

### `plan/state.json`

```json
{
  "start_date": "2026-03-21",
  "scene_ratings": {},
  "daily_log": {
    "2026-03-21": {
      "completed": ["review", "input"],
      "skipped": false
    }
  }
}
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `start_date` | ISO date string | Plan start date. All temporal values (current week, current scene, day-within-week) are computed from this field at runtime — never stored separately. |
| `scene_ratings` | object | Scene name → rating (1–5), written by `mark_done.py rating <N>` |
| `daily_log` | object | Date → `{ completed: string[], skipped: bool }` |

**Derived computations (calculated from `start_date` at runtime, never stored):**

| Value | Formula |
|-------|---------|
| `plan_day` | `(today - start_date).days + 1` (1-indexed, overall plan day) |
| `current_week` | `ceil(plan_day / 7)` |
| `day_within_week` | `((plan_day - 1) % 7) + 1` — resets 1–7 each week; shown as `Day {D}` in push headers |
| `current_scene` | Look up `current_week` in the scene roadmap table (weeks 1–2 → scene 1, etc.) |
| `scene_cycle_day` | `((plan_day - 1) % 14) + 1` — day within the current 2-week scene cycle (1–14) |
| `is_biweekly_checkin` | `scene_cycle_day == 14` |

### `plan/config.json`

```json
{
  "morning_hour": 7,
  "evening_hour": 21,
  "weekly_recording_day": "saturday",
  "timezone": "Asia/Shanghai"
}
```

`bark_token` is NOT stored here. It is read from the environment variable `BARK_TOKEN` (set as a GitHub Secret).

---

## Scene Roadmap (for task generation)

| Weeks | Scene | Podcast focus | Article source |
|-------|-------|---------------|----------------|
| 1–2   | Self-introduction & small talk | The English We Speak | BBC Worklife |
| 3–4   | Expressing opinions & discussing solutions | Business English Pod | HBR |
| 5–6   | Email writing & professional written expression | Business English Pod | HBR |
| 7–8   | Making plans & social conversation | 6 Minute English | Reddit r/jobs |
| 9–10  | Reporting progress & giving feedback | Business English Pod | HBR |
| 11–12 | Expressing emotions & storytelling | 6 Minute English | BBC Worklife |
| 13–14 | Asking questions & confirming information | The English We Speak | Reddit r/cscareerquestions |
| 15–16 | Free review & weak scene reinforcement | (resolved at runtime — see below) | (resolved at runtime — see below) |

**Weeks 15–16 scene resolution rule:**

When `current_week` is 15 or 16, `generate_task.py` selects the reinforcement scene as follows:

1. Look up all scenes that have an entry in `scene_ratings`
2. Select the scene with the lowest rating value
3. If multiple scenes share the lowest rating, select the one with the earlier week number
4. If no ratings exist at all (user skipped all check-ins), default to Scene 1 (Self-introduction & small talk)

The selected scene's podcast and article source are used unchanged from the scene roadmap.

---

## Inter-Process Message Contract

Scripts communicate via stdout/stdin using a JSON envelope. `generate_task.py` and `check_evening.py` write to stdout; `push_bark.py` reads from stdin.

**Schema:**

```json
{
  "title": "string — notification title (max 50 chars)",
  "body": "string — notification body text",
  "url": "string | null — optional deep-link URL (unused currently, set to null)"
}
```

**Example (morning):**

```json
{
  "title": "📅 Week 1 · Day 3 | Self-introduction & small talk",
  "body": "✅ Review (5min)\nOpen Anki...\n\n🎧 Input (15min)\n...",
  "url": null
}
```

`push_bark.py` maps these fields to the Bark API call:
- `title` → Bark `title` parameter
- `body` → Bark `body` parameter
- `url` → Bark `url` parameter (omitted from request if null)

---

## Push Content Format

### Morning Push (07:00)

```
📅 Week {N} · Day {D} | {Scene Name}

✅ Review (5min)
Open Anki and complete today's due cards. Review only — don't add new cards here.

🎧 Input (15min)
Podcast: {podcast name}
Search keyword: "{scene keyword}"
Listen to a 1-2 min segment. Play 3 times: once for meaning, twice while shadowing rhythm and intonation.

📖 Extraction (10min)
Source: {article source}
Search: "{scene article keyword}"
Highlight 3-5 idiomatic expressions. Add each to Anki with source sentence + your own example.

🗣️ Output (10-15min)
Send this prompt to Claude or ChatGPT:
"{AI scene simulation prompt for current scene}"

Today's budget: 35-45 min
```

### Evening Push (21:00)

```
🌙 Today's progress

{block completion icons — ✅ or ⬜ for each of Review / Input / Extraction / Output}

Completion: {N}%

Tomorrow: Week {N} · Day {D+1}
{motivational nudge if completion < 50%}
```

### Biweekly Rating Reminder (appended to evening push on Day 14 of each scene cycle)

```
📊 Biweekly check-in!

Scene completed: {scene name} (Week {N}-{N+1})

1. Compare your cold-attempt and reviewed-attempt recordings
2. Fill in your scene rating: python scripts/mark_done.py rating <1-5>
3. Decide: advance to next scene, or reinforce for one more week?
```

---

## Mark-Done CLI

```bash
python scripts/mark_done.py review      # Mark Review block complete
python scripts/mark_done.py input       # Mark Input block complete
python scripts/mark_done.py extraction  # Mark Extraction block complete
python scripts/mark_done.py output      # Mark Output block complete
python scripts/mark_done.py all         # Mark all blocks complete
python scripts/mark_done.py skip        # Mark today as skipped (no double-up)
python scripts/mark_done.py rating 4   # Submit biweekly scene rating (1-5)
```

Each command updates `state.json` and runs `git commit && git push` automatically.

**Validation rules enforced by `mark_done.py`:**
- Block names must be one of: `review`, `input`, `extraction`, `output`, `all`, `skip`
- `rating` argument must be an integer in the range [1, 5]; any other value exits with a clear error message and makes no changes to `state.json`

---

## GitHub Actions Workflows

### `morning.yml`

```yaml
on:
  schedule:
    - cron: '0 23 * * *'   # 23:00 UTC = 07:00 BJT
jobs:
  push-morning:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - run: pip install requests
      - run: python scripts/generate_task.py | python scripts/push_bark.py morning
        env:
          BARK_TOKEN: ${{ secrets.BARK_TOKEN }}
```

### `evening.yml`

```yaml
on:
  schedule:
    - cron: '0 13 * * *'   # 13:00 UTC = 21:00 BJT
jobs:
  push-evening:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - run: pip install requests
      - run: python scripts/check_evening.py | python scripts/push_bark.py evening
        env:
          BARK_TOKEN: ${{ secrets.BARK_TOKEN }}
```

---

## Error Handling

| Failure scenario | Behavior |
|-----------------|----------|
| Bark API returns non-2xx | Script exits with non-zero code; GitHub Actions marks job as failed; learner sees failed workflow in GitHub UI |
| `state.json` missing or malformed | Script exits non-zero with descriptive error message; no push sent |
| `mark_done.py` fails to `git push` (e.g., network error, conflict) | Script prints error and exits non-zero; `state.json` local change is preserved; learner retries manually |
| `BARK_TOKEN` secret not set | `push_bark.py` exits non-zero immediately with message "BARK_TOKEN environment variable not set" |

All scripts must exit non-zero on failure. Workflows use `continue-on-error: false` (GitHub default) so failures are visible in the Actions UI.

---

## Security

- `BARK_TOKEN` stored as GitHub Actions Secret only — never committed to repo
- `config.json` contains no credentials
- Repo can be public or private without risk

---

## Out of Scope

- Web UI for marking completion (CLI is sufficient)
- Multi-user support
- Automatic content fetching from podcasts/articles (links and keywords are embedded in scripts, not scraped)
- Reminder snooze or reschedule (Bark handles notification management natively)
