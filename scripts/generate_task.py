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
