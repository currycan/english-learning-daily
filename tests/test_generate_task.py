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
