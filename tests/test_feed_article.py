"""Tests for scripts/feed_article.py — Phase 2 RSS Fetch.

RED phase: all tests fail until Plan 02 creates the implementation.
"""
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from scripts.feed_article import (
    _extract_body,
    _fetch_feed,
    _select_entry,
    _try_entries,
    _validate,
    clean_html,
    fetch_article,
)


@pytest.fixture
def sample_config():
    return {
        "primary_url": "https://www.newsinlevels.com/feed",
        "fallback_url": "https://www.bbc.co.uk/learningenglish/english/features/lingohack/feed.rss",
        "content_topics": ["AI", "artificial intelligence", "technology", "international", "economy", "science", "climate"],
    }


def _make_entry(title="Test Article", summary="Short summary", link="https://example.com/article", full_content=None):
    entry = {"title": title, "summary": summary, "link": link}
    if full_content is not None:
        entry["content"] = [{"value": full_content}]
    return entry


LONG_BODY = "This is a long article body. " * 10  # 300+ chars


# --- FTCH-01: Primary feed fetch and entry selection ---

def test_fetch_primary_feed():
    """_fetch_feed returns entries list from parsed feed."""
    mock_result = MagicMock()
    mock_result.bozo = False
    mock_result.entries = [_make_entry("Entry 1"), _make_entry("Entry 2")]
    with patch("feedparser.parse", return_value=mock_result):
        entries = _fetch_feed("https://www.newsinlevels.com/feed")
    assert len(entries) == 2


def test_keyword_selection():
    """_select_entry returns first entry whose title/summary contains a keyword."""
    entries = [
        _make_entry(title="Sports news today"),
        _make_entry(title="New technology breakthrough"),
    ]
    result = _select_entry(entries, ["technology"])
    assert result["title"] == "New technology breakthrough"


def test_no_match_fallback():
    """_select_entry returns entries[0] when no keyword matches."""
    entries = [
        _make_entry(title="Sports news"),
        _make_entry(title="Local weather"),
    ]
    result = _select_entry(entries, ["xyz_nomatch_keyword"])
    assert result["title"] == "Sports news"


def test_idempotency_guard(tmp_path, monkeypatch):
    """main() exits 0 when today's content file already exists."""
    from scripts import feed_article
    fake_path = tmp_path / "2026-03-23.md"
    fake_path.write_text("exists")
    monkeypatch.setattr(feed_article, "content_path", lambda d: fake_path)
    monkeypatch.setattr(feed_article, "get_beijing_date", lambda: fake_path.stem)
    with pytest.raises(SystemExit) as exc:
        feed_article.main()
    assert exc.value.code == 0


# --- FTCH-02: Fallback and retry ---

def test_fallback_on_primary_failure(sample_config):
    """fetch_article falls back to fallback_url when primary returns no entries."""
    fallback_entries = [_make_entry(full_content=LONG_BODY)]

    def fake_fetch(url):
        if "newsinlevels" in url:
            return []
        return fallback_entries

    with patch("scripts.feed_article._fetch_feed", side_effect=fake_fetch):
        result = fetch_article(sample_config)
    assert result is not None
    assert result["title"] == "Test Article"


def test_both_feeds_fail(sample_config):
    """fetch_article exits 1 when both primary and fallback return no valid article."""
    with patch("scripts.feed_article._fetch_feed", return_value=[]):
        with pytest.raises(SystemExit) as exc:
            fetch_article(sample_config)
    assert exc.value.code == 1


def test_retry_three_entries(sample_config):
    """_try_entries returns first valid envelope within max_attempts."""
    short_entry = _make_entry(summary="Too short")
    valid_entry = _make_entry(full_content=LONG_BODY)
    entries = [short_entry, short_entry, valid_entry]
    result = _try_entries(entries, sample_config["content_topics"], max_attempts=3)
    assert result is not None
    assert len(result["body"]) >= 200


# --- FTCH-03: Extraction, cleaning, validation ---

def test_body_extraction_priority():
    """_extract_body prefers content[0].value over summary."""
    entry = _make_entry(summary="Short summary", full_content="<p>Full content text here.</p>")
    result = _extract_body(entry)
    assert "Full content text here" in result
    assert result != "Short summary"


def test_html_stripping():
    """clean_html removes all HTML tags."""
    result = clean_html("<p>Hello <strong>world</strong></p>")
    assert "<" not in result
    assert ">" not in result
    assert "Hello" in result
    assert "world" in result


def test_entity_decoding():
    """clean_html decodes HTML entities."""
    result = clean_html("AT&amp;T sells &quot;products&quot;")
    assert "AT&T" in result
    assert '"products"' in result
    assert "&amp;" not in result
    assert "&quot;" not in result


def test_validation_body_too_short():
    """_validate returns False when body is under 200 characters."""
    envelope = {"title": "Title", "body": "x" * 199, "source_url": "https://example.com"}
    assert _validate(envelope) is False


def test_output_envelope_schema(sample_config):
    """fetch_article returns dict with exactly title, body, source_url keys."""
    valid_entry = _make_entry(full_content=LONG_BODY)
    with patch("scripts.feed_article._fetch_feed", return_value=[valid_entry]):
        with patch("scripts.content_utils.content_path") as mock_cp:
            mock_cp.return_value.exists.return_value = False
            result = fetch_article(sample_config)
    assert set(result.keys()) == {"title", "body", "source_url"}
    assert result["title"].strip() != ""
    assert len(result["body"]) >= 200
    assert result["source_url"].strip() != ""
