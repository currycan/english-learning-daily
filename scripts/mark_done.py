import copy
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
