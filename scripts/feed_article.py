"""RSS article fetcher — Phase 2.

Fetches one English article per day from configured RSS feeds.
Outputs Article Envelope JSON to stdout for Phase 3 consumption.

Usage:
    python -m scripts.feed_article
"""
import html as html_module
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

import feedparser

from scripts.content_utils import get_beijing_date


class _TextExtractor(HTMLParser):
    """Private HTML parser that extracts plain text from HTML."""

    BLOCK_TAGS = {"p", "br", "div", "h1", "h2", "h3", "h4", "li"}

    def __init__(self):
        super().__init__()
        self._parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self._parts.append(data)

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag.lower() in self.BLOCK_TAGS:
            self._parts.append("\n")

    def get_text(self) -> str:
        return "".join(self._parts)


def clean_html(raw: str) -> str:
    """Strip HTML tags and decode entities from raw HTML string.

    Returns plain text with collapsed whitespace.
    """
    extractor = _TextExtractor()
    extractor.feed(raw)
    text = extractor.get_text()
    text = html_module.unescape(text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _extract_body(entry) -> str:
    """Extract raw body HTML/text from a feedparser entry.

    Priority: content[0].value > summary > description.
    """
    if entry.get("content"):
        return entry["content"][0]["value"]
    elif entry.get("summary"):
        return entry["summary"]
    else:
        return entry.get("description", "")


def _validate(envelope: dict) -> bool:
    """Return True only when title, body >= 200 chars, and source_url are all present."""
    title_ok = bool(envelope.get("title", "").strip())
    body_ok = len(envelope.get("body", "")) >= 200
    url_ok = bool(envelope.get("source_url", "").strip())
    return title_ok and body_ok and url_ok


def _fetch_feed(url: str) -> list:
    """Fetch and parse an RSS feed URL. Returns list of entries (never raises)."""
    result = feedparser.parse(url)
    if result.bozo:
        print(
            f"WARNING: feed parse error for {url}: {result.bozo_exception}",
            file=sys.stderr,
        )
    return list(result.entries)


def _select_entry(entries: list, topics: list[str]) -> dict | None:
    """Select the best entry from a list based on topic keywords.

    Pass 1: return first entry whose title+summary contains any keyword.
    Pass 2: return entries[0] if no keyword match.
    """
    topics_lower = [t.lower() for t in topics]
    for entry in entries:
        text = (
            entry.get("title", "") + " " + entry.get("summary", "")
        ).lower()
        if any(kw in text for kw in topics_lower):
            return entry
    return entries[0] if entries else None


def _try_entries(entries: list, topics: list[str], max_attempts: int = 3) -> dict | None:
    """Try up to max_attempts entries, returning the first valid envelope.

    Tries the keyword-preferred entry first, then remaining entries in order.
    Returns None if no valid envelope found within max_attempts.
    """
    candidates: list = []
    seen: set = set()

    preferred = _select_entry(entries, topics)
    if preferred is not None:
        preferred_id = id(preferred)
        candidates.append(preferred)
        seen.add(preferred_id)

    for entry in entries:
        if id(entry) not in seen:
            candidates.append(entry)
            seen.add(id(entry))

    for candidate in candidates[:max_attempts]:
        raw = _extract_body(candidate)
        body = clean_html(raw)
        envelope = {
            "title": candidate.get("title", ""),
            "body": body,
            "source_url": candidate.get("link", ""),
        }
        if _validate(envelope):
            return envelope

    return None


def fetch_article(config: dict) -> dict:
    """Fetch one article from primary or fallback feed.

    Returns a validated envelope dict with title, body, source_url.
    Exits 1 if both feeds fail to return a valid article.
    """
    primary_url = config["primary_url"]
    fallback_url = config["fallback_url"]
    topics = config["content_topics"]

    # Try primary feed
    entries = _fetch_feed(primary_url)
    result = _try_entries(entries, topics) if entries else None
    if result is not None:
        return result

    # Try fallback feed
    entries = _fetch_feed(fallback_url)
    result = _try_entries(entries, topics) if entries else None
    if result is not None:
        return result

    # Both failed
    print(
        "ERROR: both primary and fallback feeds failed to return a valid article",
        file=sys.stderr,
    )
    sys.exit(1)


def _load_config() -> dict:
    """Load content_feeds section from plan/config.json."""
    config_path = Path("plan/config.json")
    with config_path.open() as f:
        return json.load(f)["content_feeds"]


def main() -> None:
    """Entry point: fetch today's article and print JSON envelope to stdout."""
    config = _load_config()
    envelope = fetch_article(config)
    print(json.dumps(envelope))


if __name__ == "__main__":
    main()
