from datetime import date, datetime, timedelta, timezone
from pathlib import Path

BEIJING_TZ = timezone(timedelta(hours=8))
CONTENT_DIR = Path("content")


def get_beijing_date() -> date:
    """Return today's date in CST (UTC+8) regardless of runner timezone."""
    return datetime.now(tz=BEIJING_TZ).date()


def content_path(d: date) -> Path:
    """Return the canonical content file path for a given date."""
    return CONTENT_DIR / f"{d.isoformat()}.md"
