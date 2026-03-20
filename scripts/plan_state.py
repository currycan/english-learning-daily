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
