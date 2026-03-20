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

def test_save_state_oserror_raises():
    with pytest.raises(SystemExit):
        save_state({"start_date": "2026-03-21", "scene_ratings": {}, "daily_log": {}}, "/nonexistent/dir/state.json")

def test_load_state_missing_file_raises():
    with pytest.raises(SystemExit):
        load_state("/nonexistent/state.json")
