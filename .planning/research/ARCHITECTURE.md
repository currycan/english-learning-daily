# Architecture Patterns

**Domain:** Automated English learning content generation pipeline (RSS → AI → git)
**Researched:** 2026-03-22
**Confidence:** HIGH — existing codebase establishes the pattern; new system follows the same shape.

---

## Recommended Architecture

The existing codebase uses a **Unix pipeline architecture**: discrete Python scripts communicate via stdout → stdin JSON, each with a single responsibility. The new content generation system must fit this shape exactly.

The new pipeline adds one upstream stage (RSS fetch + filter) and replaces the Bark delivery stage with a git-commit stage. Everything in between follows the same module-per-concern discipline.

### High-Level Flow

```
[GitHub Actions cron]
        |
        v
 fetch_article.py          -- fetch RSS, pick one item, validate level
        |
     stdout (JSON: article envelope)
        |
        v
 generate_exercises.py     -- call Claude API, produce vocabulary + questions
        |
     stdout (JSON: content envelope)
        |
        v
 render_markdown.py        -- combine article + exercises into final Markdown
        |
     stdout (Markdown string)
        |
        v
 commit_content.py         -- write file to content/YYYY-MM-DD.md, git add/commit/push
```

Each stage is independently testable and replaceable. The GitHub Actions workflow wires them together with `|` pipes exactly as `generate_task.py | push_bark.py` does today.

---

## Component Boundaries

| Component | File | Responsibility | Input | Output |
|-----------|------|---------------|-------|--------|
| RSS Fetcher | `scripts/fetch_article.py` | Fetch feed, select one item, basic level filter | `SOURCE_URL` env var (or config) | JSON envelope: `{title, url, body, source}` |
| Exercise Generator | `scripts/generate_exercises.py` | Call Claude API, extract vocabulary + comprehension questions | JSON envelope from stdin | JSON envelope: `{article, vocabulary, questions}` |
| Markdown Renderer | `scripts/render_markdown.py` | Format combined content as Markdown | JSON envelope from stdin | Markdown string to stdout |
| Git Committer | `scripts/commit_content.py` | Write file, check for duplicates, git add/commit/push | Markdown string from stdin | Exit 0 on success, 1 on failure |
| Shared Utilities | `scripts/content_utils.py` | Date helpers, idempotency check, level-scoring heuristic | N/A (imported) | Pure functions |

### What Does Not Cross Boundaries

- The RSS fetcher does not call Claude. It outputs raw article text only.
- The exercise generator does not touch the filesystem or git. It outputs JSON only.
- The Markdown renderer does not write files. It outputs a string only.
- The git committer does not generate or format content. It only persists.

---

## Data Flow

### Envelope Formats

**Stage 1 → Stage 2: Article Envelope**
```json
{
  "title": "string",
  "url": "string",
  "body": "string",
  "source": "voa|bbc|guardian",
  "word_count": 350,
  "fetched_date": "YYYY-MM-DD"
}
```

**Stage 2 → Stage 3: Content Envelope**
```json
{
  "article": {
    "title": "string",
    "url": "string",
    "body": "string",
    "source": "string"
  },
  "vocabulary": [
    {"word": "string", "definition": "string", "example": "string"}
  ],
  "questions": [
    {"question": "string", "answer": "string"}
  ],
  "generated_date": "YYYY-MM-DD"
}
```

**Stage 3 → Stage 4: Markdown String**
Plain Markdown text on stdout. The committer writes it to `content/YYYY-MM-DD.md`.

### GitHub Actions Wiring

```yaml
- name: Generate daily lesson
  run: |
    python -m scripts.fetch_article \
    | python -m scripts.generate_exercises \
    | python -m scripts.render_markdown \
    | python -m scripts.commit_content
  env:
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

This is a direct extension of the existing `generate_task.py | push_bark.py` pattern.

---

## Patterns to Follow

### Pattern 1: Single-Concern Script with JSON Envelope

**What:** Each script reads JSON (or plain text) from stdin, does exactly one thing, writes JSON (or plain text) to stdout.

**When:** Always — every stage in the pipeline.

**Why:** Mirrors `generate_task.py` and `push_bark.py` exactly. New scripts integrate without changing the workflow model. Each script is independently testable by piping sample JSON fixtures to it.

```python
import json, sys

def main():
    raw = sys.stdin.read()
    envelope = json.loads(raw)           # validate input
    result = transform(envelope)         # do the work
    print(json.dumps(result))            # pass to next stage

if __name__ == "__main__":
    main()
```

### Pattern 2: Idempotent Output

**What:** Before writing `content/YYYY-MM-DD.md`, check if the file already exists. If it does, exit 0 with a log message — do not overwrite, do not fail.

**When:** In `commit_content.py` before any git operation.

**Why:** GitHub Actions may re-run on failure. The existing `plan/state.json` model has the same constraint (mark_done checks before writing). Prevents duplicate commits from accumulating.

```python
from pathlib import Path

def already_committed(date_str: str) -> bool:
    return Path(f"content/{date_str}.md").exists()
```

### Pattern 3: Pure Functions for Formatting Logic

**What:** Markdown assembly is a pure function: `render(content_envelope: dict) -> str`. No I/O inside it.

**When:** In `render_markdown.py` and `content_utils.py`.

**Why:** Matches the temporal functions in `plan_state.py` (pure, no I/O, easy to test). The render function can be unit-tested with a fixture dict and a string assertion — no file system or API required.

### Pattern 4: Environment-Only Secrets

**What:** `ANTHROPIC_API_KEY` read from environment at script start. Absent key → stderr message + `sys.exit(1)`.

**When:** In `generate_exercises.py` main() guard.

**Why:** Matches `BARK_TOKEN` pattern in `push_bark.py`. Fails loudly before any API call is made.

### Pattern 5: Graceful Source Fallback

**What:** If the primary RSS feed fails (network error, empty feed, no qualifying articles), the fetcher tries a secondary source before exiting non-zero.

**When:** In `fetch_article.py`.

**Why:** The existing error handling strategy is "exit non-zero on failure so GitHub Actions marks job failed." A transient VOA outage should not silence the day's lesson; one retry to BBC avoids unnecessary failures.

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: Mixing I/O and Logic in the Same Script

**What:** Having `generate_exercises.py` also write the file, or having `fetch_article.py` call Claude.

**Why bad:** Breaks the testability of each stage. Breaks the pipeline composability. Matches nothing in the existing codebase.

**Instead:** Keep each script to one concern. File write lives only in `commit_content.py`.

### Anti-Pattern 2: Storing Fetched Content in state.json

**What:** Adding `last_article_url` or `last_article_body` to `plan/state.json`.

**Why bad:** The existing architecture principle is explicit: `state.json` stores only `start_date`, `scene_ratings`, and `daily_log`. Polluting it with content data breaks that contract and creates hidden coupling between systems.

**Instead:** Use the idempotency check on the filesystem (`content/YYYY-MM-DD.md` exists) as the duplicate-detection mechanism. No shared state between systems.

### Anti-Pattern 3: Multi-Turn Claude API Calls

**What:** Making multiple API calls — one for vocabulary, one for questions — or using conversation history.

**Why bad:** Doubles cost per day. Increases latency. Adds failure surface area.

**Instead:** One prompt, one call, structured JSON output. Claude can return vocabulary array and questions array in a single response with a well-designed prompt.

### Anti-Pattern 4: Storing Raw HTML in the Pipeline

**What:** Passing raw RSS feed XML or scraped HTML between stages.

**Why bad:** RSS encodes content in `<![CDATA[...]]>` blocks with embedded HTML tags. Passing this to Claude inflates prompt tokens and produces worse output.

**Instead:** `fetch_article.py` strips to plain text before emitting. The article body in the envelope is clean prose only.

### Anti-Pattern 5: Hard-Coded RSS URLs

**What:** Embedding `feeds.voanews.com/...` as a string literal in `fetch_article.py`.

**Why bad:** Source URLs change. The existing codebase uses `plan/config.json` for non-secret configuration.

**Instead:** Read source URLs from `plan/config.json` or environment variable. Enables source swap without code change.

---

## Suggested Build Order

Dependencies between components determine the only safe build sequence.

```
1. content_utils.py          -- shared helpers, no deps; required by all others
2. fetch_article.py          -- depends on utils; can be tested with live RSS or fixture
3. generate_exercises.py     -- depends on utils; can be tested with fixture article JSON
4. render_markdown.py        -- depends on utils; pure function, easiest to test
5. commit_content.py         -- depends on utils; requires git env; test with dry-run flag
6. GitHub Actions workflow   -- wires all four stages; last because it needs all scripts
```

**Why this order:**
- `content_utils.py` first because level-scoring heuristic and date helpers are shared.
- Fetcher before generator because generator's fixture input comes from testing the fetcher.
- Renderer before committer because committer needs to consume renderer output.
- Workflow last because it is integration; unit tests for each stage come first.

---

## Component Detail: fetch_article.py

**Primary source:** VOA Learning English RSS (`feeds.voanews.com/learningenglish/english`)
**Secondary source:** BBC Learning English RSS (fallback)
**Selection:** Take the most recent item that passes the level filter.
**Level filter heuristic:** Average sentence length < 20 words AND word count 200–600. This is a proxy for B1-B2 suitability. Confidence: MEDIUM (heuristic, not validated against CEFR benchmarks — flag for phase research).
**Library:** `requests` (already in requirements.txt) + Python standard `xml.etree.ElementTree` for RSS parsing. No new dependencies needed.

---

## Component Detail: generate_exercises.py

**API:** Anthropic Claude (claude-haiku or claude-3-5-haiku — low cost for daily use)
**Call pattern:** Single synchronous POST via `anthropic` SDK
**Prompt contract:** System prompt specifies JSON schema for output. Output is parsed with `json.loads()`.
**Failure modes:** API error → stderr + `sys.exit(1)`. JSON parse failure → stderr + `sys.exit(1)`. Both cause GitHub Actions to mark job failed.
**Token budget:** ~800 tokens input (article body) + ~200 tokens instructions + ~400 tokens output. Well within Haiku limits and low daily cost.

---

## Component Detail: commit_content.py

**Idempotency check:** `Path(f"content/{today}.md").exists()` — exits 0 if already present.
**Git operations:** `git config user.email`, `git config user.name`, `git add`, `git commit`, `git push`. Mirrors `mark_done.py` pattern.
**GitHub Actions token:** `actions/checkout@v4` with `token: ${{ secrets.GITHUB_TOKEN }}` and `persist-credentials: true`. No separate deploy key needed for same-repo commits.
**Directory:** Creates `content/` directory if it does not exist before writing.

---

## Scalability Considerations

| Concern | Now (1 article/day) | If extended |
|---------|---------------------|-------------|
| API cost | ~$0.001/day with Haiku | Still negligible at 1 call/day |
| RSS reliability | Single source is fragile | Fallback list of 2-3 sources in config |
| Content duplication | Idempotency check on filename | Would need URL dedup log for same-source repeats |
| File accumulation | 365 files/year; fine for git | After years: consider yearly subdirs `content/2026/` |
| CI time | <30s per run | No concern; network + API dominates, not compute |

---

## Sources

- Existing codebase architecture: `/Users/andrew/study-all/.planning/codebase/ARCHITECTURE.md` (HIGH confidence — direct analysis)
- Existing workflow: `/Users/andrew/study-all/.github/workflows/morning.yml` (HIGH confidence — direct read)
- Project requirements: `/Users/andrew/study-all/.planning/PROJECT.md` (HIGH confidence — direct read)
- RSS→Python patterns: training knowledge, not verified against live docs (MEDIUM confidence — flag for phase research on `feedparser` vs `xml.etree` choice)
- Claude API structured output: training knowledge (MEDIUM confidence — verify `anthropic` SDK response_format support before implementation)
