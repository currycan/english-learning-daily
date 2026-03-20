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
    assert state["daily_log"][TODAY]["completed"].count("review") == 1

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

def test_apply_command_does_not_mutate_input():
    state = fresh_state()
    original_log = dict(state["daily_log"])
    apply_command(state, "review", rating=None, today=date.today())
    assert state["daily_log"] == original_log
