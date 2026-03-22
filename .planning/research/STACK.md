# Technology Stack

**Project:** English Daily Content — automated article fetch + AI exercise generation
**Researched:** 2026-03-22
**Confidence:** MEDIUM — versions from project files + training knowledge (August 2025 cutoff); web/pip verification was unavailable during this session. Flag `anthropic` SDK version for pin-before-commit.

---

## Recommended Stack

### Core Runtime

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| Python | 3.12 (CI), 3.14 local | All script logic | Already the project runtime; do not introduce a second language |
| GitHub Actions | ubuntu-latest | Scheduling + execution | Already in use for morning/evening push workflows; no new infra needed |

### HTTP / Feed Fetching

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| `requests` | 2.32.3 (pinned) | HTTP calls to RSS endpoints and Guardian API | Already pinned in requirements.txt; battle-tested, simple API, no async overhead needed for one daily call |
| `feedparser` | 6.0.11 | Parse Atom/RSS XML from VOA and BBC feeds | The canonical Python RSS library since 2004; handles malformed XML, encoding edge cases, and feed autodiscovery automatically. `requests` alone requires you to hand-roll XML parsing. |

**Why not `httpx` or `aiohttp`?** The pipeline makes one HTTP call per day from GitHub Actions. Async overhead buys nothing. `requests` is already a dependency; no reason to add a second HTTP client.

**Why `feedparser` and not raw `xml.etree`?** VOA and BBC feeds have encoding quirks and occasional malformed XML. `feedparser` is lenient-by-design (same philosophy as browsers); `xml.etree` will raise on minor violations. This avoids fragile daily job failures.

### AI / Claude API

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| `anthropic` | >=0.25.0, <1.0 | Claude API client for exercise generation | Official Anthropic Python SDK. Wraps auth, retries, and the Messages API. Using the SDK rather than raw `requests` to Anthropic's API is strongly preferred: automatic retry on rate limits, typed response objects, version stability guarantees. |

**Model to use:** `claude-haiku-3-5` (or latest Haiku). One call per day, short prompt (~500 tokens in, ~800 out). Haiku is 3x cheaper than Sonnet with 90% of the quality for structured generation tasks like vocabulary extraction. If output quality is insufficient, promote to `claude-sonnet-4-5`.

**Why not Sonnet for this?** The PROJECT.md constraint says "API costs must be minimal — one call per day, short prompt." Haiku is the correct tier.

### Content Filtering / Readability Scoring

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| stdlib `re` + heuristics | built-in | B1-B2 level pre-filter | VOA Special English is already curated for non-native speakers; a simple word-count + sentence-length heuristic (no external library) is sufficient to reject outlier articles before sending to Claude. Adding `textstat` or `readability` libraries adds a dependency for marginal gain. |

**Decision:** No readability library. Delegate B1-B2 judgment entirely to Claude in the prompt. VOA Special English as primary source eliminates most filtering work at the source level.

### Output / File Generation

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| stdlib `pathlib` | built-in | File paths and existence checks | Already used in `plan_state.py`; consistent with codebase conventions |
| stdlib `textwrap` | built-in | Markdown formatting | No external templating engine needed for simple Markdown files |

**Why not Jinja2?** The output is a single flat Markdown file per day, not a multi-template site. Jinja2 is overkill and adds a dependency.

### Git Commit Automation

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| `actions/checkout@v4` | v4 | Checkout with write permissions | Already used in existing workflows |
| `git` CLI via `subprocess` | system git | Commit and push `content/YYYY-MM-DD.md` | Already the pattern in `mark_done.py`; consistent, no new library needed |
| GitHub Actions `GITHUB_TOKEN` | — | Authenticate git push from CI | Standard pattern; no PAT needed for same-repo commits when using `actions/checkout@v4` with default permissions |

**Git identity in CI:** GitHub Actions requires `git config user.email` and `git config user.name` before committing. Set these in the workflow step, not in code.

### Testing

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| `pytest` | 8.3.5 (pinned) | Unit and integration tests | Already the project test framework |
| `pytest-cov` | 7.0.0 (pinned) | Coverage reporting | Already in use |
| `responses` or `unittest.mock` | stdlib mock preferred | Mock HTTP calls in tests | `unittest.mock.patch` is sufficient for mocking `requests.get` and `anthropic.Anthropic().messages.create`; no extra library needed |

---

## Alternatives Considered

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| RSS parsing | `feedparser` | `xml.etree.ElementTree` | Brittle on malformed feeds; no encoding handling |
| RSS parsing | `feedparser` | `lxml` | Heavier C dependency; compilation required on some CI images |
| AI client | `anthropic` SDK | `requests` to Anthropic API directly | Manual auth, retry logic, response parsing — the SDK handles all of this |
| AI model | `claude-haiku-3-5` | `claude-sonnet-4-6` | Sonnet is 3x more expensive; Haiku sufficient for structured extraction |
| Readability filtering | None (VOA + Claude prompt) | `textstat` library | Extra dependency for marginal benefit; VOA source pre-filters level |
| Markdown output | stdlib `textwrap` + f-strings | `jinja2` | Single flat template does not justify templating engine overhead |
| Git automation | `subprocess` + git CLI | `gitpython` | `gitpython` is heavier than needed; `subprocess` is already the project pattern |
| HTTP client | `requests` (existing) | `httpx` | No async needed; `requests` already pinned |

---

## Installation

```bash
# Add to requirements.txt (existing entries preserved)
feedparser==6.0.11
anthropic>=0.25.0,<1.0
```

Pin `feedparser` exactly (it is stable). Use a range for `anthropic` because the SDK releases frequently with backwards-compatible improvements; an upper bound of `<1.0` protects against a hypothetical breaking v1 API change.

**Full requirements.txt after additions:**

```
requests==2.32.3
pytest==8.3.5
pytest-cov==7.0.0
feedparser==6.0.11
anthropic>=0.25.0,<1.0
```

---

## Environment Variables Required

| Variable | Source | Used By |
|----------|--------|---------|
| `ANTHROPIC_API_KEY` | GitHub Secrets | `anthropic` SDK (auto-read from env) |
| `BARK_TOKEN` | GitHub Secrets (existing) | `push_bark.py` (existing) |
| `GITHUB_TOKEN` | Auto-provided by Actions | `git push` in content workflow |

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| `requests` version | HIGH | Pinned in existing requirements.txt |
| `pytest` / `pytest-cov` versions | HIGH | Pinned in existing requirements.txt |
| `feedparser` version 6.0.x | MEDIUM | Last known stable release per training data (Aug 2025); verify on PyPI before pinning |
| `anthropic` SDK version range | MEDIUM | SDK was at 0.25+ as of training cutoff; `<1.0` bound is conservative; verify current version before first deploy |
| Claude model `haiku-3-5` | MEDIUM | Model naming as of Aug 2025; verify current model ID against Anthropic docs at implementation time |
| GitHub Actions action versions | HIGH | `checkout@v4` and `setup-python@v5` are current stable as of Aug 2025 |

---

## Sources

- Existing `requirements.txt`: `requests==2.32.3`, `pytest==8.3.5`
- Existing `.github/workflows/morning.yml`: Python 3.12, `actions/checkout@v4`, `actions/setup-python@v5`
- `.planning/PROJECT.md`: constraint "no new runtime dependencies beyond `requests` and `anthropic` SDK"
- `.planning/codebase/STACK.md`: existing stack inventory
- `.planning/codebase/ARCHITECTURE.md`: `subprocess` + git pattern in `mark_done.py`
- Training knowledge (August 2025): `feedparser` 6.x stable, Anthropic SDK 0.25+, Haiku model tier
