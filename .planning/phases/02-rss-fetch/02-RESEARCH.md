# Phase 2: RSS Fetch - Research

**Researched:** 2026-03-23
**Domain:** Python RSS parsing, HTML cleaning, article extraction
**Confidence:** HIGH (core stack), MEDIUM (VOA feed URL — see critical warning)

## Summary

Phase 2 must produce a well-formed Article Envelope JSON (`title`, `body`, `source_url`) by fetching from an RSS feed, filtering entries by keyword, cleaning HTML from the body text, validating the result, and writing the envelope to stdout. All decisions are locked in CONTEXT.md: `feedparser` for parsing, `html.parser` for cleaning, `plan/config.json` for feed URLs, and a three-attempt retry before falling back to BBC.

The single most important finding from this research is a **critical feed URL risk**: the original VOA URL (`feeds.voanews.com/learningenglish/english`) now returns a 302 redirect to a podcast page, and all verified current VOA feed API endpoints have empty `<description>` fields — they cannot satisfy the 200-character body requirement. The BBC Learning English fallback feeds (Lingohack, 6-Minute English, News Report) similarly contain only 20–100 character teasers, not article prose. Verified research found that `newsinlevels.com/feed` provides `<content:encoded>` sections with 800+ characters of graded English prose — this is the strongest candidate for a reliable fallback. The plan must treat the feed URL as a configuration variable (already locked to `plan/config.json`) and address URL validation during Wave 0.

**Primary recommendation:** Implement `feed_article.py` against the feedparser API exactly as locked in CONTEXT.md, but verify both the primary VOA URL and the BBC fallback URL during Wave 0 using a live smoke test before trusting either returns 200-char body text. Store verified working URLs in `plan/config.json`.

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Article selection strategy**
- Keyword-first: iterate RSS entries, prefer the most recent entry whose `title` or `summary` contains a `content_topics` keyword
- No-match fallback: if no entry matches, take the most recent entry in the feed — guaranteed daily content
- Topic preferences: international news, daily conversation, AI/tech
- Initial keyword list: `["AI", "artificial intelligence", "technology", "international", "economy", "science", "climate"]` — stored in `plan/config.json` `content_topics`, no code change needed to update

**Body cleaning rules**
- Tool: Python stdlib `html.parser` — zero new dependencies
- Target format: plain text with paragraph breaks (single blank line between paragraphs); all HTML tags removed
- Delivered to Phase 3: readable natural-English prose for vocabulary and question generation

**Feed URL configuration**
- Location: existing `plan/config.json`, new `content_feeds` field (no new config file)
- Field structure:
  ```json
  "content_feeds": {
    "primary_url": "https://feeds.voanews.com/learningenglish/english",
    "fallback_url": "https://www.bbc.co.uk/learningenglish/english/features/lingohack/feed.rss",
    "content_topics": ["AI", "artificial intelligence", "technology", "international", "economy", "science", "climate"]
  }
  ```
- RSS parsing library: `feedparser` — add to `requirements.txt`

**Article validation**
- Three hard constraints (all must pass): `title` non-empty, cleaned `body` >= 200 characters, `source_url` non-empty
- Failure handling: try up to 3 entries from current feed; if all fail, switch to fallback (BBC); if BBC also fails, `sys.exit(1)` + clear stderr message

**Article Envelope JSON output**
- Via stdout (consistent with existing `push_bark.py` stdin consumer pattern)
- Schema: `{"title": "...", "body": "...", "source_url": "..."}`
- Phase 3 `generate_exercises.py` reads this via stdin pipe

### Claude's Discretion

- `feedparser` specific version pin
- Field extraction priority order from a `feedparser` entry: `content[0].value` > `summary` > `description`
- Body cleaning whitespace normalization (e.g., collapse multiple blank lines to one)

### Deferred Ideas (OUT OF SCOPE)

- Topic auto-tagging (v2 QUAL-01) — Phase 2 does keyword filter only, no tagging
- Vocabulary deduplication (QUAL-02) — post-Phase 3
- Already-read article deduplication — v2, not Phase 2
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| FTCH-01 | Fetch one article daily from VOA Special English RSS feed | feedparser 6.0.12 parses RSS 2.0; config-driven URL; keyword selection strategy locked |
| FTCH-02 | Fall back to BBC Learning English RSS if VOA fetch fails | feedparser handles both feeds identically; same extraction logic applies; fallback URL in config |
| FTCH-03 | Extract article title, full body text, and source URL from feed | feedparser fields: `entry.title`, `entry.link`, body via `content[0].value` > `summary` priority chain; HTML cleaning via `html.parser` |
</phase_requirements>

---

## Critical Warning: Feed URL Verification Required

**HIGH confidence — verified by direct fetch 2026-03-23**

| Feed URL | Status | Body Content |
|----------|--------|-------------|
| `feeds.voanews.com/learningenglish/english` | 302 redirect to podcast page | N/A — URL broken |
| `learningenglish.voanews.com/api/zkm-ql-vomx-tpej-rqi` (As It Is) | Live RSS 2.0 feed | Empty `<description>` fields — fails 200-char requirement |
| `feeds.bbci.co.uk/learningenglish/english/features/lingohack/rss` | Live RSS 2.0 feed | 80–150 chars — fails 200-char requirement |
| `feeds.bbci.co.uk/learningenglish/english/features/6-minute-english/rss` | Live RSS 2.0 feed | 30–50 chars — fails 200-char requirement |
| `feeds.bbci.co.uk/learningenglish/english/features/news-report/rss` | Live RSS 2.0 feed | 20–60 chars — fails 200-char requirement |
| `www.newsinlevels.com/feed` | Live RSS 2.0 feed | 800+ chars via `content:encoded` — PASSES 200-char requirement |

**Implication for Wave 0:** The planner MUST include a wave that verifies the configured feed URLs produce entries with 200+ character bodies before the main implementation is written. The URLs stored in `plan/config.json` must be replaced with verified working URLs. `newsinlevels.com/feed` is the only verified-working source found as of this research date.

---

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| feedparser | 6.0.12 | Parse RSS/Atom/RDF feeds | Locked decision; handles malformed XML, CDATA, character encoding; more robust than `xml.etree` |
| requests | 2.32.3 (already installed) | HTTP client (already used in project) | Already in `requirements.txt`; consistent with `push_bark.py` patterns |
| html.parser | stdlib | Strip HTML tags from body text | Locked decision; zero new dependencies; sufficient for well-formed HTML in RSS entries |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| json | stdlib | Serialize Article Envelope to stdout | Always — same pattern as `push_bark.py` |
| sys | stdlib | `sys.exit(1)` + `stderr` error output | All error paths |
| html | stdlib | `html.unescape()` for HTML entities | After stripping tags to decode `&amp;`, `&quot;`, etc. |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| feedparser | xml.etree | feedparser locked — handles malformed XML, CDATA blocks, encoding negotiation that xml.etree cannot |
| html.parser | BeautifulSoup | html.parser locked — avoids new dependency; adequate for RSS body cleanup |
| feedparser | requests + xml.etree | feedparser locked — handles the range of RSS variants in the wild |

**Installation:**
```bash
pip install feedparser==6.0.12
```
Add to `requirements.txt`: `feedparser==6.0.12`

---

## Architecture Patterns

### Recommended Project Structure

No new directories needed. One new script in the existing `scripts/` layout:

```
scripts/
├── feed_article.py      # new — Phase 2 deliverable
├── content_utils.py     # existing — import get_beijing_date(), content_path()
├── push_bark.py         # existing — reference pattern for error handling
└── ...
tests/
└── test_feed_article.py # new — TDD test file
plan/
└── config.json          # extend with content_feeds field
```

### Pattern 1: feedparser Entry Field Extraction

**What:** Extract body text from a feedparser entry using a priority chain.
**When to use:** Always — different RSS publishers use different fields for the full body.

feedparser maps RSS `<content:encoded>` to `entry.content` (a list of dicts), and RSS `<description>` to `entry.summary`. The priority order for body text extraction:

```python
# Priority: content[0].value > summary > description
def _extract_body(entry) -> str:
    """Extract raw HTML body from feedparser entry using field priority chain."""
    if entry.get("content"):
        return entry["content"][0]["value"]
    if entry.get("summary"):
        return entry["summary"]
    return entry.get("description", "")
```

Source: feedparser 6.0.12 docs — `entries[i].content` is "full content," `entries[i].summary` is "a summary of the entry."

### Pattern 2: HTML Stripping with html.parser

**What:** Strip HTML tags and decode entities from feed body text.
**When to use:** After extracting raw body — RSS descriptions and content:encoded often contain HTML markup.

```python
from html.parser import HTMLParser
import html as html_module


class _TextExtractor(HTMLParser):
    """Collect text nodes, insert newlines for block-level tags."""

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
    """Strip HTML tags, decode entities, normalise whitespace."""
    extractor = _TextExtractor()
    extractor.feed(raw)
    text = extractor.get_text()
    text = html_module.unescape(text)
    # Collapse 3+ consecutive newlines to a single blank line
    import re
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()
```

### Pattern 3: Idempotency Check (reuse content_utils.py)

**What:** Skip fetch entirely if today's content file already exists.
**When to use:** At the top of `main()`, before any network calls.

```python
from scripts.content_utils import get_beijing_date, content_path

def main() -> None:
    today = get_beijing_date()
    if content_path(today).exists():
        print(f"[feed_article] {today} already exists, skipping.", file=sys.stderr)
        sys.exit(0)
    # ... proceed with fetch
```

Source: Established project pattern from `commit_content.py` (Phase 1).

### Pattern 4: Config Loading

**What:** Load feed URLs and keywords from `plan/config.json`.
**When to use:** Once at startup in `main()`.

```python
import json
from pathlib import Path

def _load_config() -> dict:
    config_path = Path("plan/config.json")
    with config_path.open() as f:
        return json.load(f)

# Usage:
config = _load_config()
feeds = config["content_feeds"]
primary_url = feeds["primary_url"]
fallback_url = feeds["fallback_url"]
topics = feeds["content_topics"]
```

### Pattern 5: Error Path (reuse push_bark.py pattern)

**What:** All error exits print to stderr and call `sys.exit(1)`.
**When to use:** Every error path — matches existing project convention.

```python
print(f"ERROR: [description] {detail}", file=sys.stderr)
sys.exit(1)
```

### Anti-Patterns to Avoid

- **Hardcoding feed URLs:** Feed URLs must come from `plan/config.json` — VOA's URL has historically changed. Never embed them in source code.
- **Assuming `entry.summary` is always present:** Some entries have neither `summary` nor `content` — the extraction function must handle all three absent cases gracefully.
- **Storing computed fields in state.json:** Do not write anything to `plan/state.json` from this script — Phase 2 outputs to stdout only.
- **Silent failures:** Never catch an exception without either retrying, falling back, or calling `sys.exit(1)` with a clear stderr message.
- **Mutating the config dict:** Read config once, use it immutably — consistent with project immutability rules.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| RSS parsing | Custom XML parser | feedparser 6.0.12 | Handles CDATA, malformed XML, encoding negotiation, Atom/RSS/RDF variants — xml.etree fails on real-world feeds |
| HTML entity decoding | Custom regex for `&amp;` etc. | `html.unescape()` (stdlib) | Covers all named, decimal, and hex entities correctly |
| HTTP with timeout | `urllib.request` | `requests` (already in requirements) | Established project pattern; consistent timeout + status-code handling with `push_bark.py` |

**Key insight:** feedparser's value is not just XML parsing — it normalises field names across RSS 2.0, Atom 1.0, and RDF, handles CDATA-wrapped HTML bodies, and negotiates character encoding. Hand-rolling this against a single feed format will break on the first malformed response.

---

## Common Pitfalls

### Pitfall 1: Empty Description Fields in Modern RSS Feeds

**What goes wrong:** Script calls `entry.summary` or `entry.description` expecting article prose; field is empty string or absent; validation fails for every entry; script falls back and exits non-zero every day.

**Why it happens:** Modern feed publishers (including current VOA API endpoints) have moved full content behind a paywall or website — the RSS feed carries only metadata. The original VOA URL `feeds.voanews.com/learningenglish/english` now redirects. All BBC Learning English feeds tested contain descriptions under 165 chars.

**How to avoid:** During Wave 0, run a live smoke test against each configured URL: parse the feed, check whether at least one entry passes the 200-char body test. Replace non-working URLs in `plan/config.json` before implementing the full script. Only `newsinlevels.com/feed` (which uses `<content:encoded>`) was verified to pass as of this research.

**Warning signs:** Every test against a real feed returns validation failure; `len(body) == 0` or body contains metadata like `"Learning English use a limited vocabulary..."`.

### Pitfall 2: feedparser `content` vs `summary` Confusion

**What goes wrong:** Developer only checks `entry.summary`, misses `<content:encoded>` present in the feed — body is truncated to 100 chars when full text was available at `entry.content[0]["value"]`.

**Why it happens:** RSS 2.0 spec uses `<description>` for summaries and `<content:encoded>` for full text; feedparser maps these to `.summary` and `.content[0]["value"]` respectively. Many tutorials only show `.summary`.

**How to avoid:** Always apply the priority chain: `content[0].value` first, fall through to `summary`, then `description`.

**Warning signs:** Body text is truncated or ends with `"..."` but the linked article page has full text.

### Pitfall 3: HTML Tags in body Field

**What goes wrong:** `entry.summary` or `entry.content[0]["value"]` contains `<p>`, `<strong>`, `<br>` tags; AI in Phase 3 receives markup instead of clean prose; vocabulary extraction is confused by tag strings.

**Why it happens:** RSS `<content:encoded>` commonly stores full HTML including paragraph and formatting tags. feedparser returns the value as-is (sanitised but still HTML).

**How to avoid:** Always run `clean_html()` on the raw body value before validation and output. feedparser does sanitise dangerous tags (script, style) but does NOT strip structural HTML.

**Warning signs:** `body` field in output JSON contains `<p>` or `&nbsp;` or `<br>` substrings.

### Pitfall 4: VOA URL Instability

**What goes wrong:** Hardcoded URL stops working; CI fails every day; no fallback path for the primary source.

**Why it happens:** VOA's domain structure has changed at least twice. The original `feeds.voanews.com/learningenglish/english` redirects as of March 2026. VOA's organizational status has been volatile in 2025-2026.

**How to avoid:** All URLs in `plan/config.json` — never hardcoded. Treat both `primary_url` and `fallback_url` as configuration that may need updating. Include a Wave 0 step to validate both URLs before writing implementation.

**Warning signs:** `feedparser.parse(url)` returns `feed.bozo == True` and `feed.bozo_exception` is a redirect or connection error; `len(feed.entries) == 0`.

### Pitfall 5: feedparser `bozo` Flag Not Checked

**What goes wrong:** feedparser silently returns a partial or empty result for a malformed/redirected feed; script selects no entries; exits non-zero.

**Why it happens:** feedparser sets `feed.bozo = True` for any parse error or HTTP error, but does NOT raise an exception — it returns a best-effort result. Code that doesn't check `bozo` may not notice a broken feed.

**How to avoid:** After `feedparser.parse(url)`, check both `feed.bozo` (log as warning if True) and `len(feed.entries) > 0` (exit or fall back if False).

```python
import feedparser

def _fetch_feed(url: str) -> list:
    """Parse feed; return entries or empty list on failure."""
    result = feedparser.parse(url)
    if result.bozo:
        print(f"WARNING: feed parse error for {url}: {result.bozo_exception}", file=sys.stderr)
    return result.entries
```

---

## Code Examples

Verified patterns from official sources and project conventions:

### Article Envelope Output (stdout JSON pattern)

```python
# Source: scripts/push_bark.py — established project pattern
import json, sys

envelope = {"title": title, "body": body, "source_url": source_url}
print(json.dumps(envelope))          # stdout — consumed by Phase 3 via pipe
```

### feedparser Entry Iteration with Keyword Filtering

```python
# Source: feedparser 6.0.12 docs + project CONTEXT.md decisions
import feedparser

def _select_entry(entries: list, topics: list[str]) -> dict | None:
    """Return best matching entry: keyword match first, else most recent."""
    topics_lower = [t.lower() for t in topics]

    # Pass 1: keyword match in title or summary
    for entry in entries:
        text = f"{entry.get('title', '')} {entry.get('summary', '')}".lower()
        if any(kw in text for kw in topics_lower):
            return entry

    # Pass 2: most recent (first entry in feed — feeds are newest-first)
    return entries[0] if entries else None
```

### Article Validation

```python
# Source: CONTEXT.md locked decisions
def _validate(envelope: dict) -> bool:
    """All three conditions must hold."""
    return (
        bool(envelope.get("title", "").strip()) and
        len(envelope.get("body", "")) >= 200 and
        bool(envelope.get("source_url", "").strip())
    )
```

### Three-Attempt Entry Retry

```python
# Source: CONTEXT.md locked decisions
def _try_entries(entries: list, topics: list[str], max_attempts: int = 3) -> dict | None:
    """Try up to max_attempts entries; return first valid envelope or None."""
    candidates = _rank_entries(entries, topics)   # keyword matches first
    for entry in candidates[:max_attempts]:
        envelope = _build_envelope(entry)
        if _validate(envelope):
            return envelope
    return None
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `feeds.voanews.com/learningenglish/english` | URL redirects — use `learningenglish.voanews.com/api/...` | ~2024–2025 | Original URL broken; new API endpoints have empty descriptions |
| BBC Lingohack full-text | BBC feeds contain only short teasers (<165 chars) | Unknown — observed March 2026 | Neither BBC fallback passes 200-char body test with current feed content |
| RSS full-text in `<description>` | Many publishers moved to `<content:encoded>` for full text | ~2015+ | Must check `entry.content[0]["value"]` first |

**Deprecated/outdated:**
- `feeds.voanews.com/learningenglish/english`: Redirects to podcast page as of March 2026. Do not use.
- Relying on `entry.description` alone: Modern full-text feeds use `<content:encoded>` mapped to `entry.content`.

---

## Open Questions

1. **Verified working feed URL for primary slot**
   - What we know: `feeds.voanews.com/learningenglish/english` is broken. Current VOA API feeds have empty description fields. `newsinlevels.com/feed` has `content:encoded` with 800+ chars.
   - What's unclear: Whether VOA will restore full-text RSS (possible given March 2026 court order restoring staff). Whether `newsinlevels.com` content meets topic-keyword preferences (international/AI/tech — it leans toward general interest stories).
   - Recommendation: Wave 0 must include a live feed URL validation step. Update `plan/config.json` with the working URL. Use `newsinlevels.com/feed` as primary or fallback until a VOA full-text source is confirmed.

2. **Fallback URL body content**
   - What we know: `https://www.bbc.co.uk/learningenglish/english/features/lingohack/feed.rss` (the URL locked in CONTEXT.md) has not been verified to return 200+ char body text — all tested BBC Learning English feeds had short teasers.
   - What's unclear: Whether the exact URL in CONTEXT.md differs from the tested URLs (`feeds.bbci.co.uk` domain vs `www.bbc.co.uk` domain).
   - Recommendation: Wave 0 should test `https://www.bbc.co.uk/learningenglish/english/features/lingohack/feed.rss` directly with feedparser and measure description lengths. If it also fails the 200-char test, update fallback URL to `newsinlevels.com/feed`.

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 8.3.5 |
| Config file | `pytest.ini` / project root (no separate config found — uses default discovery) |
| Quick run command | `pytest tests/test_feed_article.py -x` |
| Full suite command | `pytest` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| FTCH-01 | feedparser parses primary feed URL and returns at least one entry | unit (mock requests) | `pytest tests/test_feed_article.py::test_fetch_primary_feed -x` | ❌ Wave 0 |
| FTCH-01 | keyword filter selects matching entry from parsed entries | unit | `pytest tests/test_feed_article.py::test_keyword_selection -x` | ❌ Wave 0 |
| FTCH-01 | no-match fallback returns most recent entry | unit | `pytest tests/test_feed_article.py::test_no_match_fallback -x` | ❌ Wave 0 |
| FTCH-01 | idempotency guard exits 0 when today's file already exists | unit | `pytest tests/test_feed_article.py::test_idempotency_guard -x` | ❌ Wave 0 |
| FTCH-02 | VOA failure triggers fallback to BBC feed | unit (mock feedparser) | `pytest tests/test_feed_article.py::test_fallback_on_primary_failure -x` | ❌ Wave 0 |
| FTCH-02 | both feeds fail → sys.exit(1) with stderr message | unit | `pytest tests/test_feed_article.py::test_both_feeds_fail -x` | ❌ Wave 0 |
| FTCH-02 | three-attempt retry before fallback | unit | `pytest tests/test_feed_article.py::test_retry_three_entries -x` | ❌ Wave 0 |
| FTCH-03 | content[0].value > summary > description priority chain | unit | `pytest tests/test_feed_article.py::test_body_extraction_priority -x` | ❌ Wave 0 |
| FTCH-03 | HTML tags stripped from body | unit | `pytest tests/test_feed_article.py::test_html_stripping -x` | ❌ Wave 0 |
| FTCH-03 | HTML entities decoded in body | unit | `pytest tests/test_feed_article.py::test_entity_decoding -x` | ❌ Wave 0 |
| FTCH-03 | validation rejects body < 200 chars | unit | `pytest tests/test_feed_article.py::test_validation_body_too_short -x` | ❌ Wave 0 |
| FTCH-03 | stdout JSON contains title, body, source_url fields | unit | `pytest tests/test_feed_article.py::test_output_envelope_schema -x` | ❌ Wave 0 |
| All | live smoke: configured feed URL returns valid envelope | integration (live network) | `python -m scripts.feed_article` (manual — requires network) | manual-only |

### Sampling Rate

- **Per task commit:** `pytest tests/test_feed_article.py -x`
- **Per wave merge:** `pytest`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps

- [ ] `tests/test_feed_article.py` — all FTCH-01/02/03 unit tests (12 tests above)
- [ ] `plan/config.json` — add `content_feeds` field with verified working URLs (see Open Questions)
- [ ] `feedparser==6.0.12` in `requirements.txt` — not yet present
- [ ] Manual smoke: run `python -m scripts.feed_article` against live feed URLs; confirm envelope body >= 200 chars and JSON is valid

---

## Sources

### Primary (HIGH confidence)
- feedparser 6.0.12 PyPI page — version confirmed September 2025
- feedparser docs `entries[i].content` — content field structure and MIME type handling
- feedparser docs `entries[i].summary` — summary vs content distinction
- Direct feed fetch 2026-03-23: `feeds.bbci.co.uk/learningenglish/english/features/lingohack/rss` — confirmed live, confirmed short descriptions
- Direct feed fetch 2026-03-23: `feeds.bbci.co.uk/learningenglish/english/features/6-minute-english/rss` — confirmed live, confirmed short descriptions
- Direct feed fetch 2026-03-23: `learningenglish.voanews.com/api/zkm-ql-vomx-tpej-rqi` — confirmed live, confirmed empty descriptions
- Direct fetch 2026-03-23: `feeds.voanews.com/learningenglish/english` → 302 redirect confirmed
- Direct feed fetch 2026-03-23: `www.newsinlevels.com/feed` — confirmed live, content:encoded has 800+ chars

### Secondary (MEDIUM confidence)
- DEV Community article on HTMLParser — clean text extraction pattern with `handle_data()` + `html.unescape()`
- feedparser docs "Common RSS Elements" — confirms `entry.title`, `entry.link`, `entry.published` field names

### Tertiary (LOW confidence)
- WebSearch result: VOA organizational status March 2026 (court order restoring 1,000+ employees) — context on why VOA feeds may recover, but unverified effect on RSS content

---

## Metadata

**Confidence breakdown:**
- Standard stack (feedparser, html.parser, requests): HIGH — feedparser version confirmed on PyPI; field names confirmed in official docs; html.parser pattern confirmed against published code
- Architecture (entry extraction, retry, fallback): HIGH — directly derived from locked CONTEXT.md decisions; field priority confirmed in docs
- Feed URL reliability: LOW — original VOA URL broken; BBC fallback unverified for 200-char body; only newsinlevels.com verified to pass body validation
- Common pitfalls: HIGH — all confirmed by direct feed inspection 2026-03-23

**Research date:** 2026-03-23
**Valid until:** 2026-04-07 (30 days for stack; 7 days for feed URL status — recheck VOA status before planning)
