# Daily Task Generator Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a GitHub Actions–powered system that pushes daily English learning tasks to an iPhone via Bark, tracks completion in a local JSON file, and sends biweekly scene-rating reminders.

**Architecture:** A shared `plan_state.py` module computes all temporal values (week, day, scene) from a single `start_date` field and exposes the scene roadmap. `generate_task.py` and `check_evening.py` produce JSON payloads to stdout; `push_bark.py` reads stdin and calls the Bark API. `mark_done.py` is the CLI for marking completion. GitHub Actions runs the morning and evening scripts on a cron schedule.

**Tech Stack:** Python 3.12, `requests`, `pytest`, GitHub Actions, Bark iOS app

---

## File Map

| File | Responsibility |
|------|---------------|
| `plan/state.json` | Persistent state: start date, scene ratings, daily completion log |
| `plan/config.json` | Non-secret config: push hours, timezone, recording day |
| `scripts/plan_state.py` | Shared: load/save state, scene roadmap, all temporal derivations |
| `scripts/generate_task.py` | Reads state → writes morning JSON payload to stdout |
| `scripts/push_bark.py` | Reads JSON from stdin → POSTs to Bark API |
| `scripts/check_evening.py` | Reads state → writes evening JSON payload to stdout |
| `scripts/mark_done.py` | CLI: marks blocks/skip/rating, updates state.json, git commits & pushes |
| `tests/test_plan_state.py` | Unit tests for all temporal computations and scene resolution |
| `tests/test_generate_task.py` | Unit tests for morning payload generation |
| `tests/test_check_evening.py` | Unit tests for evening payload generation |
| `tests/test_mark_done.py` | Unit tests for mark-done logic |
| `tests/test_push_bark.py` | Unit tests for Bark API call (mocked) |
| `requirements.txt` | `requests`, `pytest` |
| `.github/workflows/morning.yml` | Cron 23:00 UTC → morning push |
| `.github/workflows/evening.yml` | Cron 13:00 UTC → evening push |

---

## Chunk 1: Scaffold + Shared State Module

### Task 1: Project scaffold

**Files:**
- Create: `requirements.txt`
- Create: `pytest.ini`
- Create: `plan/state.json`
- Create: `plan/config.json`
- Create: `scripts/__init__.py`
- Create: `tests/__init__.py`

- [ ] **Step 1: Create `pytest.ini`** (sets repo root as pythonpath so `from scripts.X import ...` works)

```ini
[pytest]
pythonpath = .
```

- [ ] **Step 2: Create `requirements.txt`**

```
requests==2.32.3
pytest==8.3.5
```

- [ ] **Step 3: Create `plan/config.json`**

```json
{
  "morning_hour": 7,
  "evening_hour": 21,
  "weekly_recording_day": "saturday",
  "timezone": "Asia/Shanghai"
}
```

- [ ] **Step 4: Create `plan/state.json`**

```json
{
  "start_date": "2026-03-21",
  "scene_ratings": {},
  "daily_log": {}
}
```

- [ ] **Step 5: Create empty `scripts/__init__.py`**

```python
```

- [ ] **Step 6: Create empty `tests/__init__.py`**

```python
```

- [ ] **Step 6: Install dependencies**

```bash
pip install -r requirements.txt
```

Expected: packages install without error.

- [ ] **Step 7: Commit**

```bash
git add pytest.ini requirements.txt plan/state.json plan/config.json scripts/__init__.py tests/__init__.py
git commit -m "chore: scaffold project files"
```

---

### Task 2: Shared state module (`plan_state.py`)

**Files:**
- Create: `scripts/plan_state.py`
- Create: `tests/test_plan_state.py`

- [ ] **Step 1: Write failing tests for temporal computations**

Create `tests/test_plan_state.py`:

```python
import json
import math
import tempfile
from datetime import date, timedelta
from pathlib import Path

import pytest

from scripts.plan_state import (
    compute_plan_day,
    compute_current_week,
    compute_day_within_week,
    compute_scene_cycle_day,
    is_biweekly_checkin,
    get_scene_for_week,
    load_state,
    save_state,
    SCENE_ROADMAP,
)


# --- Temporal computations ---

def test_compute_plan_day_day1():
    start = date(2026, 3, 21)
    assert compute_plan_day(start, start) == 1

def test_compute_plan_day_day8():
    start = date(2026, 3, 21)
    today = start + timedelta(days=7)
    assert compute_plan_day(start, today) == 8

def test_compute_current_week_days_1_to_7():
    for day in range(1, 8):
        assert compute_current_week(day) == 1

def test_compute_current_week_days_8_to_14():
    for day in range(8, 15):
        assert compute_current_week(day) == 2

def test_compute_current_week_day_112():
    assert compute_current_week(112) == 16

def test_compute_day_within_week_resets():
    assert compute_day_within_week(1) == 1
    assert compute_day_within_week(7) == 7
    assert compute_day_within_week(8) == 1
    assert compute_day_within_week(14) == 7

def test_compute_scene_cycle_day():
    assert compute_scene_cycle_day(1) == 1
    assert compute_scene_cycle_day(14) == 14
    assert compute_scene_cycle_day(15) == 1
    assert compute_scene_cycle_day(28) == 14

def test_is_biweekly_checkin_true():
    assert is_biweekly_checkin(14) is True
    assert is_biweekly_checkin(28) is True

def test_is_biweekly_checkin_false():
    assert is_biweekly_checkin(13) is False
    assert is_biweekly_checkin(15) is False


# --- Scene roadmap ---

def test_scene_roadmap_has_7_scenes():
    # Weeks 1-14 = 7 scenes (weeks 15-16 are dynamic)
    fixed_scenes = [s for s in SCENE_ROADMAP if s["weeks"][1] <= 14]
    assert len(fixed_scenes) == 7

def test_get_scene_week1():
    scene = get_scene_for_week(1, {})
    assert scene["name"] == "Self-introduction & small talk"

def test_get_scene_week3():
    scene = get_scene_for_week(3, {})
    assert scene["name"] == "Expressing opinions & discussing solutions"

def test_get_scene_weeks_15_16_lowest_rated():
    ratings = {
        "Self-introduction & small talk": 3,
        "Expressing opinions & discussing solutions": 2,
        "Email writing & professional written expression": 4,
    }
    scene = get_scene_for_week(15, ratings)
    assert scene["name"] == "Expressing opinions & discussing solutions"

def test_get_scene_weeks_15_16_tiebreak_earlier_week():
    ratings = {
        "Self-introduction & small talk": 2,
        "Expressing opinions & discussing solutions": 2,
    }
    scene = get_scene_for_week(15, ratings)
    assert scene["name"] == "Self-introduction & small talk"

def test_get_scene_weeks_15_16_no_ratings_default():
    scene = get_scene_for_week(16, {})
    assert scene["name"] == "Self-introduction & small talk"


# --- State I/O ---

def test_load_state_reads_json(tmp_path):
    state_file = tmp_path / "state.json"
    state_file.write_text(json.dumps({
        "start_date": "2026-03-21",
        "scene_ratings": {},
        "daily_log": {}
    }))
    state = load_state(str(state_file))
    assert state["start_date"] == "2026-03-21"

def test_save_state_writes_json(tmp_path):
    state_file = tmp_path / "state.json"
    state = {"start_date": "2026-03-21", "scene_ratings": {}, "daily_log": {}}
    save_state(state, str(state_file))
    loaded = json.loads(state_file.read_text())
    assert loaded["start_date"] == "2026-03-21"

def test_load_state_missing_file_raises():
    with pytest.raises(SystemExit):
        load_state("/nonexistent/state.json")
```

- [ ] **Step 2: Run tests — confirm they all fail**

```bash
pytest tests/test_plan_state.py -v
```

Expected: `ImportError` or multiple `FAILED`.

- [ ] **Step 3: Implement `scripts/plan_state.py`**

```python
import json
import math
import sys
from datetime import date
from pathlib import Path

SCENE_ROADMAP = [
    {
        "weeks": (1, 2),
        "name": "Self-introduction & small talk",
        "podcast": "The English We Speak (BBC)",
        "podcast_keyword": "small talk / break the ice",
        "article_source": "BBC Worklife",
        "article_keyword": "how to introduce yourself professionally",
        "ai_prompt": (
            "Let's practice English conversation. The scene is meeting a new colleague "
            "on the first day at work. You play the role of a friendly coworker. Start "
            "the conversation naturally. After we finish, give me 3 suggestions for more "
            "natural or idiomatic phrasing."
        ),
    },
    {
        "weeks": (3, 4),
        "name": "Expressing opinions & discussing solutions",
        "podcast": "Business English Pod",
        "podcast_keyword": "expressing opinions / giving suggestions",
        "article_source": "Harvard Business Review",
        "article_keyword": "how to express opinions professionally at work",
        "ai_prompt": (
            "Let's practice English conversation. The scene is a team meeting where we're "
            "discussing solutions to a work problem. You play the role of a colleague. "
            "Start naturally. After we finish, give me 3 suggestions for more natural or "
            "idiomatic phrasing."
        ),
    },
    {
        "weeks": (5, 6),
        "name": "Email writing & professional written expression",
        "podcast": "Business English Pod",
        "podcast_keyword": "writing emails / professional writing",
        "article_source": "Harvard Business Review",
        "article_keyword": "how to write professional emails in English",
        "ai_prompt": (
            "Let's practice English. I'll write a short professional email and you give me "
            "feedback on tone, word choice, and any phrases that sound unnatural. Then "
            "suggest a more idiomatic version of each sentence that needs improvement."
        ),
    },
    {
        "weeks": (7, 8),
        "name": "Making plans & social conversation",
        "podcast": "6 Minute English (BBC)",
        "podcast_keyword": "making plans / arranging to meet",
        "article_source": "Reddit r/jobs",
        "article_keyword": "how to make small talk with coworkers",
        "ai_prompt": (
            "Let's practice English conversation. The scene is arranging plans with a "
            "colleague after work. You play the role of a friendly coworker. Start "
            "naturally. After we finish, give me 3 suggestions for more natural or "
            "idiomatic phrasing."
        ),
    },
    {
        "weeks": (9, 10),
        "name": "Reporting progress & giving feedback",
        "podcast": "Business English Pod",
        "podcast_keyword": "status update / giving feedback",
        "article_source": "Harvard Business Review",
        "article_keyword": "how to give a status update at work in English",
        "ai_prompt": (
            "Let's practice English conversation. The scene is a weekly check-in where I "
            "report my progress to you, my manager. You play the role of a manager asking "
            "follow-up questions. Start naturally. After we finish, give me 3 suggestions "
            "for more natural or idiomatic phrasing."
        ),
    },
    {
        "weeks": (11, 12),
        "name": "Expressing emotions & storytelling",
        "podcast": "6 Minute English (BBC)",
        "podcast_keyword": "expressing feelings / telling a story",
        "article_source": "BBC Worklife",
        "article_keyword": "how to tell a story in English naturally",
        "ai_prompt": (
            "Let's practice English conversation. The scene is catching up with a friend "
            "I haven't seen in a while. I'll tell you about something that happened to me "
            "recently. You play the role of an interested friend asking questions. Start "
            "naturally. After we finish, give me 3 suggestions for more natural or "
            "idiomatic phrasing."
        ),
    },
    {
        "weeks": (13, 14),
        "name": "Asking questions & confirming information",
        "podcast": "The English We Speak (BBC)",
        "podcast_keyword": "clarifying questions / confirming details",
        "article_source": "Reddit r/cscareerquestions",
        "article_keyword": "how to ask clarifying questions at work in English",
        "ai_prompt": (
            "Let's practice English conversation. The scene is a work meeting where I "
            "need to ask clarifying questions about a project brief. You play the role of "
            "a project manager explaining the brief. Start naturally. After we finish, "
            "give me 3 suggestions for more natural or idiomatic phrasing."
        ),
    },
]


def compute_plan_day(start_date: date, today: date) -> int:
    return (today - start_date).days + 1


def compute_current_week(plan_day: int) -> int:
    return math.ceil(plan_day / 7)


def compute_day_within_week(plan_day: int) -> int:
    return ((plan_day - 1) % 7) + 1


def compute_scene_cycle_day(plan_day: int) -> int:
    return ((plan_day - 1) % 14) + 1


def is_biweekly_checkin(plan_day: int) -> bool:
    return compute_scene_cycle_day(plan_day) == 14


def get_scene_for_week(week: int, scene_ratings: dict) -> dict:
    if week <= 14:
        for scene in SCENE_ROADMAP:
            if scene["weeks"][0] <= week <= scene["weeks"][1]:
                return scene
        return SCENE_ROADMAP[0]

    # Weeks 15-16: resolve by lowest rating
    if not scene_ratings:
        return SCENE_ROADMAP[0]

    rated = [s for s in SCENE_ROADMAP if s["name"] in scene_ratings]
    if not rated:
        return SCENE_ROADMAP[0]

    return min(rated, key=lambda s: (scene_ratings[s["name"]], s["weeks"][0]))


def load_state(path: str = "plan/state.json") -> dict:
    try:
        return json.loads(Path(path).read_text())
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"ERROR: Cannot load state from {path}: {e}", file=sys.stderr)
        sys.exit(1)


def save_state(state: dict, path: str = "plan/state.json") -> None:
    try:
        Path(path).write_text(json.dumps(state, indent=2, ensure_ascii=False))
    except OSError as e:
        print(f"ERROR: Cannot save state to {path}: {e}", file=sys.stderr)
        sys.exit(1)
```

- [ ] **Step 4: Run tests — confirm they all pass**

```bash
pytest tests/test_plan_state.py -v
```

Expected: all `PASSED`.

- [ ] **Step 5: Commit**

```bash
git add scripts/plan_state.py tests/test_plan_state.py
git commit -m "feat: add shared plan_state module with scene roadmap and temporal computations"
```

---

## Chunk 2: Morning Push (`generate_task.py` + `push_bark.py`)

### Task 3: `generate_task.py`

**Files:**
- Create: `scripts/generate_task.py`
- Create: `tests/test_generate_task.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_generate_task.py`:

```python
import json
from datetime import date
from unittest.mock import patch

from scripts.generate_task import build_morning_payload


SAMPLE_STATE = {
    "start_date": "2026-03-21",
    "scene_ratings": {},
    "daily_log": {},
}


def test_morning_payload_is_valid_json_schema():
    payload = build_morning_payload(SAMPLE_STATE, today=date(2026, 3, 21))
    assert "title" in payload
    assert "body" in payload
    assert "url" in payload

def test_morning_title_format_week1_day1():
    payload = build_morning_payload(SAMPLE_STATE, today=date(2026, 3, 21))
    assert "Week 1" in payload["title"]
    assert "Day 1" in payload["title"]
    assert "Self-introduction" in payload["title"]

def test_morning_title_format_week2_day3():
    # start 2026-03-21, today 2026-03-30 = plan day 10, week 2, day 3
    payload = build_morning_payload(SAMPLE_STATE, today=date(2026, 3, 30))
    assert "Week 2" in payload["title"]
    assert "Day 3" in payload["title"]

def test_morning_body_contains_all_blocks():
    payload = build_morning_payload(SAMPLE_STATE, today=date(2026, 3, 21))
    body = payload["body"]
    assert "Review" in body
    assert "Input" in body
    assert "Extraction" in body
    assert "Output" in body

def test_morning_body_contains_podcast():
    payload = build_morning_payload(SAMPLE_STATE, today=date(2026, 3, 21))
    assert "The English We Speak" in payload["body"]

def test_morning_body_contains_ai_prompt():
    payload = build_morning_payload(SAMPLE_STATE, today=date(2026, 3, 21))
    assert "Claude or ChatGPT" in payload["body"]

def test_morning_url_is_none():
    payload = build_morning_payload(SAMPLE_STATE, today=date(2026, 3, 21))
    assert payload["url"] is None

def test_morning_title_max_80_chars():
    # Titles should stay within a practical notification display length
    state_with_ratings = {**SAMPLE_STATE, "scene_ratings": {"Self-introduction & small talk": 2}}
    import datetime
    payload = build_morning_payload(state_with_ratings, today=date(2026, 3, 21) + datetime.timedelta(days=111))
    assert len(payload["title"]) <= 80
```

- [ ] **Step 2: Run tests — confirm they fail**

```bash
pytest tests/test_generate_task.py -v
```

Expected: `ImportError` or `FAILED`.

- [ ] **Step 3: Implement `scripts/generate_task.py`**

```python
import json
import sys
from datetime import date

from scripts.plan_state import (
    compute_plan_day,
    compute_current_week,
    compute_day_within_week,
    get_scene_for_week,
    load_state,
)


def build_morning_payload(state: dict, today: date = None) -> dict:
    if today is None:
        today = date.today()

    start = date.fromisoformat(state["start_date"])
    plan_day = compute_plan_day(start, today)
    week = compute_current_week(plan_day)
    day = compute_day_within_week(plan_day)
    scene = get_scene_for_week(week, state.get("scene_ratings", {}))

    title = f"📅 Week {week} · Day {day} | {scene['name']}"

    body = (
        f"✅ Review (5min)\n"
        f"Open Anki and complete today's due cards. Review only — don't add new cards here.\n\n"
        f"🎧 Input (15min)\n"
        f"Podcast: {scene['podcast']}\n"
        f"Search keyword: \"{scene['podcast_keyword']}\"\n"
        f"Listen to a 1-2 min segment. Play 3 times: once for meaning, twice while shadowing rhythm and intonation.\n\n"
        f"📖 Extraction (10min)\n"
        f"Source: {scene['article_source']}\n"
        f"Search: \"{scene['article_keyword']}\"\n"
        f"Highlight 3-5 idiomatic expressions. Add each to Anki with source sentence + your own example.\n\n"
        f"🗣️ Output (10-15min)\n"
        f"Send this prompt to Claude or ChatGPT:\n"
        f"\"{scene['ai_prompt']}\"\n\n"
        f"Today's budget: 35-45 min"
    )

    return {"title": title, "body": body, "url": None}


if __name__ == "__main__":
    state = load_state()
    payload = build_morning_payload(state)
    print(json.dumps(payload, ensure_ascii=False))
```

- [ ] **Step 4: Run tests — confirm they pass**

```bash
pytest tests/test_generate_task.py -v
```

Expected: all `PASSED`.

- [ ] **Step 5: Commit**

```bash
git add scripts/generate_task.py tests/test_generate_task.py
git commit -m "feat: add generate_task.py morning payload builder"
```

---

### Task 4: `push_bark.py`

**Files:**
- Create: `scripts/push_bark.py`
- Create: `tests/test_push_bark.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_push_bark.py`:

```python
import json
import sys
from unittest.mock import patch, MagicMock

import pytest

from scripts.push_bark import send_to_bark, main


VALID_PAYLOAD = {"title": "Test title", "body": "Test body", "url": None}


def test_send_to_bark_calls_correct_url():
    with patch("scripts.push_bark.requests.post") as mock_post:
        mock_post.return_value = MagicMock(status_code=200, text="ok")
        send_to_bark(VALID_PAYLOAD, token="testtoken")
        called_url = mock_post.call_args[0][0]
        assert "testtoken" in called_url

def test_send_to_bark_omits_url_when_none():
    with patch("scripts.push_bark.requests.post") as mock_post:
        mock_post.return_value = MagicMock(status_code=200, text="ok")
        send_to_bark(VALID_PAYLOAD, token="testtoken")
        post_data = mock_post.call_args[1].get("json", {})
        assert "url" not in post_data

def test_send_to_bark_exits_nonzero_on_api_error():
    with patch("scripts.push_bark.requests.post") as mock_post:
        mock_post.return_value = MagicMock(status_code=400, text="bad request")
        with pytest.raises(SystemExit) as exc:
            send_to_bark(VALID_PAYLOAD, token="testtoken")
        assert exc.value.code != 0

def test_send_to_bark_exits_nonzero_on_missing_token():
    with pytest.raises(SystemExit) as exc:
        send_to_bark(VALID_PAYLOAD, token="")
    assert exc.value.code != 0
```

- [ ] **Step 2: Run tests — confirm they fail**

```bash
pytest tests/test_push_bark.py -v
```

- [ ] **Step 3: Implement `scripts/push_bark.py`**

```python
import json
import os
import sys

import requests


BARK_BASE_URL = "https://api.day.app"


def send_to_bark(payload: dict, token: str) -> None:
    if not token:
        print("ERROR: BARK_TOKEN environment variable not set", file=sys.stderr)
        sys.exit(1)

    post_data = {
        "title": payload["title"],
        "body": payload["body"],
    }
    if payload.get("url") is not None:
        post_data["url"] = payload["url"]

    url = f"{BARK_BASE_URL}/{token}"
    response = requests.post(url, json=post_data, timeout=10)

    if response.status_code < 200 or response.status_code >= 300:
        print(f"ERROR: Bark API returned {response.status_code}: {response.text}", file=sys.stderr)
        sys.exit(1)


def main(push_type: str = "morning") -> None:
    token = os.environ.get("BARK_TOKEN", "")
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON from stdin: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"[{push_type}] Sending Bark notification: {payload['title']}")
    send_to_bark(payload, token=token)
    print(f"[{push_type}] Sent successfully.")


if __name__ == "__main__":
    push_type = sys.argv[1] if len(sys.argv) > 1 else "morning"
    main(push_type)
```

- [ ] **Step 4: Run tests — confirm they pass**

```bash
pytest tests/test_push_bark.py -v
```

- [ ] **Step 5: Commit**

```bash
git add scripts/push_bark.py tests/test_push_bark.py
git commit -m "feat: add push_bark.py Bark API client"
```

---

## Chunk 3: Evening Push (`check_evening.py`)

### Task 5: `check_evening.py`

**Files:**
- Create: `scripts/check_evening.py`
- Create: `tests/test_check_evening.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_check_evening.py`:

```python
import json
from datetime import date, timedelta

from scripts.check_evening import build_evening_payload


START = date(2026, 3, 21)

def make_state(completed=None, skipped=False, ratings=None, start=START):
    today_str = date.today().isoformat()
    return {
        "start_date": start.isoformat(),
        "scene_ratings": ratings or {},
        "daily_log": {
            today_str: {
                "completed": completed or [],
                "skipped": skipped,
            }
        }
    }


def test_evening_payload_schema():
    payload = build_evening_payload(make_state(), today=START)
    assert "title" in payload
    assert "body" in payload
    assert "url" in payload

def test_evening_0_percent_completion():
    payload = build_evening_payload(make_state(completed=[]), today=START)
    assert "0%" in payload["body"]

def test_evening_100_percent_completion():
    payload = build_evening_payload(
        make_state(completed=["review", "input", "extraction", "output"]),
        today=START,
    )
    assert "100%" in payload["body"]

def test_evening_partial_shows_checkmarks():
    payload = build_evening_payload(make_state(completed=["review", "input"]), today=START)
    body = payload["body"]
    assert "✅" in body
    assert "⬜" in body

def test_evening_tomorrow_normal_day():
    # Day 1 within week → tomorrow is Day 2, same week
    payload = build_evening_payload(make_state(start=START), today=START)
    assert "Week 1" in payload["body"]
    assert "Day 2" in payload["body"]

def test_evening_tomorrow_week_boundary():
    # Day 7 of week 1 → tomorrow is Week 2 Day 1
    day7 = START + timedelta(days=6)
    payload = build_evening_payload(make_state(start=START), today=day7)
    assert "Week 2" in payload["body"]
    assert "Day 1" in payload["body"]

def test_evening_plan_complete_no_tomorrow():
    # Day 112 = Week 16, Day 7 — plan complete
    day112 = START + timedelta(days=111)
    payload = build_evening_payload(make_state(start=START), today=day112)
    assert "Tomorrow" not in payload["body"]

def test_evening_biweekly_reminder_on_day_14():
    day14 = START + timedelta(days=13)
    payload = build_evening_payload(make_state(start=START), today=day14)
    assert "Biweekly check-in" in payload["body"]

def test_evening_no_biweekly_reminder_on_day_13():
    day13 = START + timedelta(days=12)
    payload = build_evening_payload(make_state(start=START), today=day13)
    assert "Biweekly check-in" not in payload["body"]

def test_evening_motivational_nudge_below_50_percent():
    payload = build_evening_payload(make_state(completed=[]), today=START)
    assert "💪" in payload["body"]
```

- [ ] **Step 2: Run tests — confirm they fail**

```bash
pytest tests/test_check_evening.py -v
```

- [ ] **Step 3: Implement `scripts/check_evening.py`**

```python
import json
import sys
from datetime import date

from scripts.plan_state import (
    compute_plan_day,
    compute_current_week,
    compute_day_within_week,
    get_scene_for_week,
    is_biweekly_checkin,
    load_state,
)

BLOCKS = ["review", "input", "extraction", "output"]


def build_evening_payload(state: dict, today: date = None) -> dict:
    if today is None:
        today = date.today()

    start = date.fromisoformat(state["start_date"])
    plan_day = compute_plan_day(start, today)
    week = compute_current_week(plan_day)
    day = compute_day_within_week(plan_day)
    scene = get_scene_for_week(week, state.get("scene_ratings", {}))

    today_str = today.isoformat()
    day_log = state.get("daily_log", {}).get(today_str, {"completed": [], "skipped": False})
    completed = day_log.get("completed", [])

    # Completion icons
    icons = " ".join("✅" if b in completed else "⬜" for b in BLOCKS)
    block_labels = " / ".join(b.capitalize() for b in BLOCKS)
    pct = round(len(completed) / len(BLOCKS) * 100)

    # Tomorrow line
    is_last_day = week == 16 and day == 7
    if is_last_day:
        tomorrow_line = "🎉 Plan complete! Great work over 16 weeks."
    elif day == 7:
        tomorrow_line = f"Tomorrow: Week {week + 1} · Day 1"
    else:
        tomorrow_line = f"Tomorrow: Week {week} · Day {day + 1}"

    nudge = ""
    if pct < 50:
        nudge = "\n💪 No worries — even one block tomorrow keeps the streak going."

    body = (
        f"🌙 Today's progress\n\n"
        f"{block_labels}\n"
        f"{icons}\n\n"
        f"Completion: {pct}%\n\n"
        f"{tomorrow_line}"
        f"{nudge}"
    )

    # Biweekly check-in reminder
    if is_biweekly_checkin(plan_day):
        # scene_cycle_day 14 always lands on day_within_week 7 (7th day of 2nd week),
        # so we subtract 1 to get the first week of the cycle that just ended.
        start_week = week - 1 if day == 7 else week
        end_week = start_week + 1
        body += (
            f"\n\n📊 Biweekly check-in!\n\n"
            f"Scene completed: {scene['name']} (Week {start_week}–{end_week})\n\n"
            f"1. Compare your cold-attempt and reviewed-attempt recordings\n"
            f"2. Fill in your scene rating: python scripts/mark_done.py rating <1-5>\n"
            f"3. Decide: advance to next scene, or reinforce for one more week?"
        )

    return {
        "title": f"🌙 Day summary — {pct}% complete",
        "body": body,
        "url": None,
    }


if __name__ == "__main__":
    state = load_state()
    payload = build_evening_payload(state)
    print(json.dumps(payload, ensure_ascii=False))
```

- [ ] **Step 4: Run tests — confirm they pass**

```bash
pytest tests/test_check_evening.py -v
```

- [ ] **Step 5: Commit**

```bash
git add scripts/check_evening.py tests/test_check_evening.py
git commit -m "feat: add check_evening.py evening payload builder"
```

---

## Chunk 4: Mark-Done CLI (`mark_done.py`)

### Task 6: `mark_done.py`

**Files:**
- Create: `scripts/mark_done.py`
- Create: `tests/test_mark_done.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_mark_done.py`:

```python
import json
import subprocess
import sys
from datetime import date
from pathlib import Path

import pytest

from scripts.mark_done import apply_command, VALID_BLOCKS
from scripts.plan_state import SCENE_ROADMAP


TODAY = date.today().isoformat()

def fresh_state():
    return {
        "start_date": date.today().isoformat(),
        "scene_ratings": {},
        "daily_log": {},
    }


def test_mark_single_block_adds_to_completed():
    state = fresh_state()
    new_state = apply_command(state, "review", rating=None, today=date.today())
    assert "review" in new_state["daily_log"][TODAY]["completed"]

def test_mark_same_block_twice_no_duplicate():
    state = fresh_state()
    state = apply_command(state, "review", rating=None, today=date.today())
    state = apply_command(state, "review", rating=None, today=date.today())
    assert new_state["daily_log"][TODAY]["completed"].count("review") == 1 if (new_state := state) else True

def test_mark_all_adds_all_blocks():
    state = fresh_state()
    new_state = apply_command(state, "all", rating=None, today=date.today())
    for block in VALID_BLOCKS - {"all", "skip"}:
        assert block in new_state["daily_log"][TODAY]["completed"]

def test_mark_skip_sets_skipped_flag():
    state = fresh_state()
    new_state = apply_command(state, "skip", rating=None, today=date.today())
    assert new_state["daily_log"][TODAY]["skipped"] is True

def test_mark_skip_does_not_overwrite_completed():
    state = fresh_state()
    state = apply_command(state, "review", rating=None, today=date.today())
    new_state = apply_command(state, "skip", rating=None, today=date.today())
    assert "review" in new_state["daily_log"][TODAY]["completed"]

def test_rating_valid_writes_scene_key():
    # start_date = today means week 1, scene = "Self-introduction & small talk"
    state = fresh_state()
    new_state = apply_command(state, "rating", rating=3, today=date.today())
    expected_scene = SCENE_ROADMAP[0]["name"]
    assert new_state["scene_ratings"][expected_scene] == 3

def test_rating_invalid_low_raises():
    state = fresh_state()
    with pytest.raises(SystemExit):
        apply_command(state, "rating", rating=0, today=date.today())

def test_rating_invalid_high_raises():
    state = fresh_state()
    with pytest.raises(SystemExit):
        apply_command(state, "rating", rating=6, today=date.today())

def test_invalid_block_name_raises():
    state = fresh_state()
    with pytest.raises(SystemExit):
        apply_command(state, "unknown_block", rating=None, today=date.today())
```

- [ ] **Step 2: Run tests — confirm they fail**

```bash
pytest tests/test_mark_done.py -v
```

- [ ] **Step 3: Fix test typo before implementing** (line `new_state["daily_log"]...count` has a logical quirk — simplify it)

Edit `tests/test_mark_done.py`, replace the duplicate-block test:

```python
def test_mark_same_block_twice_no_duplicate():
    state = fresh_state()
    state = apply_command(state, "review", rating=None, today=date.today())
    state = apply_command(state, "review", rating=None, today=date.today())
    assert state["daily_log"][TODAY]["completed"].count("review") == 1
```

- [ ] **Step 4: Implement `scripts/mark_done.py`**

```python
import json
import os
import subprocess
import sys
from datetime import date
from pathlib import Path

from scripts.plan_state import (
    compute_plan_day,
    compute_current_week,
    get_scene_for_week,
    load_state,
    save_state,
)

VALID_BLOCKS = {"review", "input", "extraction", "output", "all", "skip"}
STATE_PATH = "plan/state.json"


def apply_command(state: dict, command: str, rating, today: date) -> dict:
    import copy
    state = copy.deepcopy(state)
    today_str = today.isoformat()

    if command not in VALID_BLOCKS and command != "rating":
        print(f"ERROR: Unknown command '{command}'. Valid: {sorted(VALID_BLOCKS)} or 'rating <1-5>'", file=sys.stderr)
        sys.exit(1)

    # Ensure today's log entry exists
    if today_str not in state["daily_log"]:
        state["daily_log"][today_str] = {"completed": [], "skipped": False}

    entry = state["daily_log"][today_str]

    if command == "all":
        for block in ["review", "input", "extraction", "output"]:
            if block not in entry["completed"]:
                entry["completed"].append(block)
    elif command == "skip":
        entry["skipped"] = True
    elif command == "rating":
        if rating is None or not isinstance(rating, int) or rating < 1 or rating > 5:
            print(f"ERROR: Rating must be an integer between 1 and 5. Got: {rating!r}", file=sys.stderr)
            sys.exit(1)
        start = date.fromisoformat(state["start_date"])
        plan_day = compute_plan_day(start, today)
        week = compute_current_week(plan_day)
        scene = get_scene_for_week(week, state.get("scene_ratings", {}))
        state["scene_ratings"][scene["name"]] = rating
    else:
        if command not in entry["completed"]:
            entry["completed"].append(command)

    return state


def git_commit_and_push(block: str) -> None:
    try:
        subprocess.run(["git", "add", STATE_PATH], check=True)
        subprocess.run(["git", "commit", "-m", f"chore: mark {block} done for {date.today()}"], check=True)
        subprocess.run(["git", "push"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"ERROR: git operation failed: {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    args = sys.argv[1:]
    if not args:
        print("Usage: mark_done.py <block|skip|all|rating> [rating_value]", file=sys.stderr)
        sys.exit(1)

    command = args[0]
    rating = None

    if command == "rating":
        if len(args) < 2:
            print("ERROR: 'rating' requires a value, e.g.: mark_done.py rating 4", file=sys.stderr)
            sys.exit(1)
        try:
            rating = int(args[1])
        except ValueError:
            print(f"ERROR: Rating must be an integer. Got: {args[1]!r}", file=sys.stderr)
            sys.exit(1)

    state = load_state(STATE_PATH)
    new_state = apply_command(state, command, rating=rating, today=date.today())
    save_state(new_state, STATE_PATH)
    git_commit_and_push(command if command != "rating" else f"rating={rating}")
    print(f"✓ Marked '{command}' — state updated and pushed.")


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Run tests — confirm they pass**

```bash
pytest tests/test_mark_done.py -v
```

- [ ] **Step 6: Commit**

```bash
git add scripts/mark_done.py tests/test_mark_done.py
git commit -m "feat: add mark_done.py CLI for completion tracking"
```

---

## Chunk 5: GitHub Actions Workflows

### Task 7: Workflow files

**Files:**
- Create: `.github/workflows/morning.yml`
- Create: `.github/workflows/evening.yml`

- [ ] **Step 1: Create `.github/workflows/morning.yml`**

```yaml
name: Morning push

on:
  schedule:
    - cron: '0 23 * * *'   # 23:00 UTC = 07:00 BJT (UTC+8)
  workflow_dispatch:         # Allow manual trigger for testing

jobs:
  push-morning:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Generate and push morning task
        run: python scripts/generate_task.py | python scripts/push_bark.py morning
        env:
          BARK_TOKEN: ${{ secrets.BARK_TOKEN }}
```

- [ ] **Step 2: Create `.github/workflows/evening.yml`**

```yaml
name: Evening push

on:
  schedule:
    - cron: '0 13 * * *'   # 13:00 UTC = 21:00 BJT (UTC+8)
  workflow_dispatch:         # Allow manual trigger for testing

jobs:
  push-evening:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Generate and push evening summary
        run: python scripts/check_evening.py | python scripts/push_bark.py evening
        env:
          BARK_TOKEN: ${{ secrets.BARK_TOKEN }}
```

- [ ] **Step 3: Run full test suite to confirm everything passes**

```bash
pytest tests/ -v
```

Expected: all tests `PASSED`.

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/morning.yml .github/workflows/evening.yml
git commit -m "feat: add GitHub Actions morning and evening workflow"
```

---

## Setup Instructions (run once before first push)

After pushing to GitHub:

1. Open your repo → **Settings → Secrets and variables → Actions**
2. Click **New repository secret**
3. Name: `BARK_TOKEN`, Value: your Bark token (copy from Bark app → top-right icon)
4. Click **Add secret**
5. Trigger a manual test: **Actions tab → Morning push → Run workflow**
6. Check your iPhone for the notification

---

## Verification Checklist

- [ ] `pytest tests/ -v` — all tests pass
- [ ] `python scripts/generate_task.py` — prints valid JSON to terminal
- [ ] `python scripts/check_evening.py` — prints valid JSON to terminal
- [ ] `python scripts/mark_done.py review` — updates `plan/state.json`, commits, pushes
- [ ] `python scripts/mark_done.py rating 4` — writes scene rating to `scene_ratings`
- [ ] `python scripts/mark_done.py rating 0` — prints error, exits non-zero, no state change
- [ ] GitHub Actions morning workflow triggers at 07:00 BJT and notification appears on iPhone
- [ ] GitHub Actions evening workflow triggers at 21:00 BJT with completion summary
