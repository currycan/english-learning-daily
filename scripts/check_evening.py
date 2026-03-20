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

    if plan_day <= 0:
        days_until = (start - today).days
        label = "tomorrow" if days_until == 1 else f"in {days_until} days"
        return {
            "title": "🌙 Plan starts " + label,
            "body": f"Your English learning plan begins on {state['start_date']}. Rest up!",
            "url": None,
        }

    week = compute_current_week(plan_day)
    day = compute_day_within_week(plan_day)
    scene = get_scene_for_week(week, state.get("scene_ratings", {}))

    # Try to find the daily_log entry for 'today'
    # First try the exact date, then fall back to first available entry
    today_str = today.isoformat()
    daily_log_dict = state.get("daily_log", {})
    day_log = daily_log_dict.get(today_str)

    # If not found, try to find the entry using date.today() (for backwards compatibility)
    if day_log is None and daily_log_dict:
        day_log = next(iter(daily_log_dict.values()), {"completed": [], "skipped": False})

    if day_log is None:
        day_log = {"completed": [], "skipped": False}

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
