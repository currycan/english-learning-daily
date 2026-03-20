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
