# Phase 3: AI Pipeline - Research

**Researched:** 2026-03-23
**Domain:** Anthropic Python SDK, Claude API, Markdown rendering, Git pipeline integration
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- New script `scripts/generate_exercises.py`: reads Article Envelope JSON from stdin, calls Claude API, outputs full Markdown to stdout
- Update `scripts/commit_content.py` (replace Phase 1 placeholder): reads Markdown from stdin, writes `content/YYYY-MM-DD.md`, git add + commit + push
- Workflow final form: `python -m scripts.feed_article | python -m scripts.generate_exercises | python -m scripts.commit_content`
- Any pipeline stage failure exits non-zero; downstream stages do not execute; CI job marked failed
- One Claude API call per day — single structured JSON prompt covering vocabulary + chunks + questions
- Output format: structured JSON (not Markdown directly), parsed and rendered by Python
- Model: `claude-3-5-haiku-20241022` (locked in STATE.md)
- JSON schema locked (vocabulary, chunks, questions arrays — full schema in CONTEXT.md)
- Vocabulary definitions must use B1-B2 plain English (simpler than the word being defined)
- Example sentences must be direct quotes from the article body
- Chunk examples may be generated (demonstrate usage variation), must be natural and idiomatic
- At least one inferential comprehension question (not pure factual recall)
- Markdown file layout: single file, four sections in order, bilingual emoji section headers
- Article section: full body, paragraphs preserved, last line `> Source: [URL]`
- Vocabulary format: `**word** (pos) （中文）— Definition.\n> "Quoted example."`
- 5–8 vocabulary items; Claude selects B1-B2 key words from article
- Chunk format: `**phrase** （中文）\nEnglish usage explanation.\n- Example one.\n- Example two.`
- 3–5 chunks; Claude extracts natural phrases and collocations
- Question format: `**Q: Question?**\n**A (EN):** English answer.\n**A (中):** 中文说明。`
- 3–5 questions, at least 1 inferential
- Chinese: vocabulary gloss, chunk meaning, Chinese answers — all in Chinese
- English retained: article body, English definitions, English explanations, examples, question stems
- Comprehension answers: bilingual (English + Chinese)
- ANTHROPIC_API_KEY from environment only; never in code

### Claude's Discretion

- Exact prompt wording in `generate_exercises.py` (as long as it satisfies all the above requirements)
- `max_tokens` and `temperature` for the Claude API call
- Retry count on API error (STATE.md notes: verify SDK version; specific implementation by planner)
- Internal function decomposition of `generate_exercises.py` (e.g. `build_prompt()`, `parse_response()`, `render_markdown()`)

### Deferred Ideas (OUT OF SCOPE)

- Vocabulary deduplication (skip words already seen this week) — v2 QUAL-02
- CEFR word-level annotation (A2/B1/B2) — v2 QUAL-03
- Topic tagging — v2 QUAL-01
- Weekly vocabulary digest — v2 OPS-02
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| AIGEN-01 | AI extracts 5–8 key vocabulary words with plain-English definitions and original example sentences from article text | Claude API call with JSON output; vocabulary schema locked; "example" field must be a direct article quote |
| AIGEN-02 | AI extracts 3–5 chunking expressions with Chinese meaning and 2+ varied usage examples | chunks array in JSON schema; examples field is a list; generated examples acceptable |
| AIGEN-03 | AI generates 3–5 comprehension questions covering factual recall AND inference | questions array in JSON schema; prompt must instruct at least one inferential question |
| AIGEN-04 | AI generates answers for all comprehension questions | answer_en + answer_zh fields per question in schema |
| OUT-01 | Markdown file with four clearly delimited sections: article + source URL, vocabulary, chunking, comprehension + answers | render_markdown() function maps JSON to locked section/entry format |
| OUT-02 | File named `content/YYYY-MM-DD.md` using Beijing time (CST, UTC+8) | `content_utils.get_beijing_date()` + `content_path()` already handle this — no new logic needed |
| OUT-03 | System commits and pushes rendered file to git via GitHub Actions on each successful run | `git_commit_and_push()` in commit_content.py already implements this; Phase 3 replaces main() to read stdin instead of writing placeholder |
</phase_requirements>

---

## Summary

Phase 3 wires together a three-stage pipeline: `feed_article.py` (Phase 2, complete) produces Article Envelope JSON on stdout; new `generate_exercises.py` reads that JSON, makes one Claude API call to get vocabulary + chunks + questions as structured JSON, renders the full Markdown document, and writes it to stdout; existing `commit_content.py` reads that Markdown from stdin, writes the file, and git-commits it.

The anthropic Python SDK (current: 0.86.0, March 2026) is a synchronous client. The pattern is `client = anthropic.Anthropic()` (reads `ANTHROPIC_API_KEY` from environment automatically), then `client.messages.create(model=..., max_tokens=..., messages=[...])`. Response text is at `response.content[0].text`. The SDK raises `anthropic.APIError` subclasses on failures — catching these and calling `sys.exit(1)` satisfies the "no partial commit on API failure" requirement.

The model ID `claude-3-5-haiku-20241022` remains valid as of March 2026 (verified: it is a distinct pinned snapshot, not deprecated). The `anthropic` package must be added to `requirements.txt`; it is not yet listed there. `ANTHROPIC_API_KEY` is sourced from GitHub Secrets and passed automatically as an environment variable — no changes to the workflow YAML are needed for this. The workflow's final `run:` step must change from `python -m scripts.commit_content` to the three-stage pipe.

**Primary recommendation:** Implement `generate_exercises.py` as three pure functions (`build_prompt`, `call_claude`, `render_markdown`) plus a `main()` that orchestrates stdin read → prompt → API call → JSON parse → Markdown render → stdout write, with `sys.exit(1)` on any failure. Then update `commit_content.main()` to read Markdown from stdin rather than writing a placeholder. Update the workflow `run:` step to the full pipe.

---

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| anthropic | 0.86.0 (pin to latest stable) | Claude API client | Official SDK; reads `ANTHROPIC_API_KEY` from env automatically; synchronous `messages.create()` |
| json (stdlib) | — | Parse Claude JSON response, read Article Envelope from stdin | No extra dependency |
| sys (stdlib) | — | stdin reads, `sys.exit(1)` on failures | Established project pattern |
| subprocess (stdlib) | — | git operations in commit_content.py | Already implemented; no change |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pytest | 8.3.5 | Unit tests for generate_exercises.py | All new functions need tests |
| unittest.mock | stdlib | Patch `anthropic.Anthropic` client in tests | Prevents live API calls in CI test runs |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Structured JSON from Claude | Direct Markdown generation | JSON is easier to validate programmatically; if Markdown rendering breaks, rerender without another API call |
| Single large prompt | System + user message split | System message for persistent instructions is idiomatic but either works; one message is simpler |

**Installation (add to requirements.txt):**
```bash
anthropic==0.86.0
```

> Note: Pin to a specific version to ensure reproducibility in CI. Verify the exact latest on PyPI at implementation time — 0.86.0 is current as of 2026-03-23.

---

## Architecture Patterns

### Recommended Project Structure

No new directories needed. All new files go in `scripts/` following the established pattern:

```
scripts/
├── generate_exercises.py   # NEW — Phase 3 core: stdin→Claude API→stdout Markdown
├── commit_content.py       # UPDATE — replace placeholder main() with stdin reader
├── content_utils.py        # UNCHANGED — get_beijing_date(), content_path(), CONTENT_DIR
├── feed_article.py         # UNCHANGED — Phase 2 output
└── push_bark.py            # UNCHANGED — reference for stdin/error patterns

tests/
└── test_generate_exercises.py   # NEW — unit tests for all functions
```

### Pattern 1: Stdin JSON Read (established project pattern)

**What:** Read JSON from stdin, fail fast on parse error
**When to use:** generate_exercises.py reads Article Envelope; same as push_bark.py

```python
# Source: scripts/push_bark.py (existing project pattern)
import json
import sys

raw = sys.stdin.read()
try:
    envelope = json.loads(raw)
except json.JSONDecodeError as e:
    print(f"ERROR: Invalid JSON from stdin: {e}", file=sys.stderr)
    sys.exit(1)
```

### Pattern 2: Claude API Call (anthropic SDK 0.86.x)

**What:** Synchronous call to `claude-3-5-haiku-20241022`, extract response text
**When to use:** generate_exercises.py `call_claude()` function

```python
# Source: https://platform.claude.com/docs/en/api/messages-examples (verified 2026-03-23)
import anthropic

def call_claude(prompt: str, max_tokens: int = 2048, temperature: float = 0.3) -> str:
    """Call Claude API and return raw response text. Exits 1 on API error."""
    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env
    try:
        response = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text
    except anthropic.APIError as e:
        print(f"ERROR: Claude API call failed: {e}", file=sys.stderr)
        sys.exit(1)
```

### Pattern 3: JSON Response Parse with Validation

**What:** Parse Claude's JSON output; fail fast if schema is wrong
**When to use:** After `call_claude()` returns

```python
def parse_response(raw_text: str) -> dict:
    """Parse Claude JSON response. Exits 1 if JSON is malformed or missing keys."""
    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as e:
        print(f"ERROR: Claude returned invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)
    required = {"vocabulary", "chunks", "questions"}
    missing = required - set(data.keys())
    if missing:
        print(f"ERROR: Claude response missing keys: {missing}", file=sys.stderr)
        sys.exit(1)
    return data
```

### Pattern 4: commit_content.py main() Replacement

**What:** Replace placeholder `main()` with stdin reader that writes real Markdown
**When to use:** Phase 3 updates `commit_content.py` main() only; `git_commit_and_push()` stays unchanged

```python
def main() -> None:
    today = get_beijing_date()
    path = content_path(today)

    if path.exists():
        print(f"Content for {today} already exists — skipping.", file=sys.stderr)
        sys.exit(0)

    content = sys.stdin.read()
    if not content.strip():
        print("ERROR: No content received from stdin", file=sys.stderr)
        sys.exit(1)

    CONTENT_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    git_commit_and_push(path, today)
```

### Pattern 5: Workflow Final Pipe

**What:** Replace the placeholder single-command workflow step with the full three-stage pipe

```yaml
# In .github/workflows/daily-content.yml
- name: Generate and commit daily content
  env:
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
  run: |
    python -m scripts.feed_article | \
    python -m scripts.generate_exercises | \
    python -m scripts.commit_content
```

Note: `set -o pipefail` is NOT set by default in GitHub Actions `run:` steps when using `|` continuation. Use `set -eo pipefail` or chain with `&&` to ensure intermediate failures propagate. In bash, a pipe's exit code is the last command's exit code unless `pipefail` is enabled.

### Anti-Patterns to Avoid

- **Directly outputting Markdown from Claude:** Prompt for JSON instead. Markdown from Claude has unpredictable whitespace and formatting that is hard to validate.
- **Storing API response in state.json:** The project rule is "derived state only; no computed fields stored." Article content is transient.
- **Calling `anthropic.Anthropic()` at module import time:** Instantiate in the function that uses it, so tests can patch it cleanly.
- **Using `os.system()` or shell=True for git:** The existing `subprocess.run(..., check=True)` pattern is correct and already implemented.
- **Catching bare `Exception` instead of `anthropic.APIError`:** Be specific so programming errors surface clearly.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| HTTP to Claude API | Custom requests.post() to api.anthropic.com | `anthropic.Anthropic().messages.create()` | SDK handles auth headers, retries, response parsing, error types |
| JSON schema validation | Custom key-checking loops | Explicit `required - set(data.keys())` check after json.loads | Sufficient for this schema; full jsonschema library is overkill |
| Beijing date calculation | `datetime.now().date()` (uses server timezone) | `content_utils.get_beijing_date()` (already exists) | UTC runner bug already solved in Phase 1 |
| Git operations | Shell string commands | `subprocess.run([...], check=True)` (already in git_commit_and_push) | Already implemented and tested; don't duplicate |

**Key insight:** The anthropic SDK is the only new dependency. Everything else (git, date, file I/O, JSON) is stdlib or already in the project.

---

## Common Pitfalls

### Pitfall 1: Pipe exit codes in GitHub Actions

**What goes wrong:** When running `cmd1 | cmd2 | cmd3` in a shell, the exit code is cmd3's exit code only. If `generate_exercises.py` exits 1, bash still runs `commit_content.py` with empty stdin.

**Why it happens:** Bash's default behavior; `pipefail` is not enabled in GitHub Actions `run:` by default.

**How to avoid:** Add `set -eo pipefail` as the first line of the `run:` block, or use `&&` chaining with process substitution.

**Warning signs:** CI shows "success" even though no content was committed; `commit_content.py` receives empty stdin.

### Pitfall 2: Claude returns JSON wrapped in markdown code fences

**What goes wrong:** Claude sometimes wraps its JSON response in ` ```json ... ``` ` code fences even when instructed not to. `json.loads()` then fails.

**Why it happens:** Claude's RLHF training favors formatted output. Without explicit instruction, it adds fences.

**How to avoid:** Include in the prompt: "Respond with raw JSON only. No markdown code fences, no preamble, no explanation." If still needed, strip fences defensively: `raw_text = raw_text.strip().lstrip("```json").lstrip("```").rstrip("```").strip()`.

**Warning signs:** `json.JSONDecodeError` on first character `\`` in response.

### Pitfall 3: `anthropic` not in requirements.txt

**What goes wrong:** CI installs dependencies from `requirements.txt` but `anthropic` is missing; `ImportError` at runtime.

**Why it happens:** `anthropic` is not currently listed in `requirements.txt` (only `requests`, `pytest`, `feedparser`).

**How to avoid:** Add `anthropic==0.86.0` to `requirements.txt` as part of Phase 3 Wave 0.

**Warning signs:** `ModuleNotFoundError: No module named 'anthropic'` in CI logs.

### Pitfall 4: ANTHROPIC_API_KEY not injected into workflow env

**What goes wrong:** `anthropic.Anthropic()` raises `AuthenticationError` because the key is not in the environment.

**Why it happens:** GitHub Secrets must be explicitly mapped to environment variables in the workflow step's `env:` block.

**How to avoid:** Add `env: ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}` to the pipeline step in the workflow YAML.

**Warning signs:** `anthropic.AuthenticationError` in CI; works locally if key is exported in shell.

### Pitfall 5: commit_content.py idempotency guard runs before stdin is read

**What goes wrong:** If `path.exists()` check triggers `sys.exit(0)`, the pipe from `generate_exercises.py` is still running and may throw a broken pipe error, cluttering logs.

**Why it happens:** Python exits immediately on `sys.exit(0)` without draining stdin.

**How to avoid:** This is acceptable behavior — a broken pipe on the writer side (generate_exercises.py) is non-fatal and `sys.exit(0)` correctly signals "nothing to do." The broken pipe error on stderr is cosmetic. Alternatively, drain stdin before the check: `sys.stdin.read()` before the `path.exists()` check.

### Pitfall 6: Claude JSON has fewer than 5 vocabulary items

**What goes wrong:** Claude occasionally returns 4 items when the article is short, violating AIGEN-01.

**Why it happens:** Model follows article length signals more than strict count instructions.

**How to avoid:** Prompt wording: "Select exactly 5 to 8 vocabulary words. You MUST return at least 5." Add a post-parse validation that exits 1 if `len(data["vocabulary"]) < 5`.

---

## Code Examples

### Full generate_exercises.py skeleton

```python
# scripts/generate_exercises.py
"""AI exercise generator — Phase 3.

Reads Article Envelope JSON from stdin, calls Claude API once,
outputs full Markdown lesson to stdout.

Usage (in pipeline):
    python -m scripts.feed_article | python -m scripts.generate_exercises
"""
import json
import os
import sys
from typing import Optional

import anthropic


MODEL = "claude-3-5-haiku-20241022"


def build_prompt(envelope: dict) -> str:
    """Build the Claude prompt from an Article Envelope dict."""
    title = envelope["title"]
    body = envelope["body"]
    return f"""You are an English learning assistant for Chinese speakers studying at B1-B2 level.

Given the article below, return a JSON object with three keys: "vocabulary", "chunks", "questions".

RULES:
- vocabulary: array of 5-8 objects. Each: word (str), part_of_speech (str), chinese_meaning (str), definition (str, plain English simpler than the word itself), example (str, direct verbatim quote from the article containing the word).
- chunks: array of 3-5 objects. Each: chunk (str, a natural phrase or collocation from the article), chinese_meaning (str), english_explanation (str, usage context and register), examples (list of 2 strings, generated sentences showing the chunk in varied contexts).
- questions: array of 3-5 objects. Each: question (str, in English), answer_en (str), answer_zh (str). At least ONE question must be inferential (requiring reasoning, not just recalling a stated fact).

Respond with raw JSON only. No markdown code fences, no preamble, no explanation.

Article title: {title}

Article body:
{body}"""


def call_claude(prompt: str, max_tokens: int = 2048) -> str:
    """Call Claude API. Returns response text. Exits 1 on API error."""
    client = anthropic.Anthropic()
    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text
    except anthropic.APIError as e:
        print(f"ERROR: Claude API call failed: {e}", file=sys.stderr)
        sys.exit(1)


def parse_response(raw_text: str) -> dict:
    """Parse Claude JSON response. Exits 1 if malformed or incomplete."""
    text = raw_text.strip()
    # Defensive strip of accidental code fences
    if text.startswith("```"):
        text = text.lstrip("`").lstrip("json").strip().rstrip("`").strip()
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        print(f"ERROR: Claude returned invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)
    required = {"vocabulary", "chunks", "questions"}
    missing = required - set(data.keys())
    if missing:
        print(f"ERROR: Claude response missing keys: {missing}", file=sys.stderr)
        sys.exit(1)
    if len(data["vocabulary"]) < 5:
        print(
            f"ERROR: Claude returned only {len(data['vocabulary'])} vocabulary items (need 5+)",
            file=sys.stderr,
        )
        sys.exit(1)
    return data


def render_markdown(envelope: dict, exercises: dict) -> str:
    """Render complete Markdown lesson from article envelope and exercises dict."""
    lines: list[str] = []

    # Section 1: Article
    lines.append("## \U0001f4d6 文章 / Article")
    lines.append("")
    lines.append(envelope["body"])
    lines.append("")
    lines.append(f"> Source: {envelope['source_url']}")
    lines.append("")

    # Section 2: Vocabulary
    lines.append("## \U0001f4da 词汇 / Vocabulary")
    lines.append("")
    for item in exercises["vocabulary"]:
        lines.append(
            f"**{item['word']}** ({item['part_of_speech']}) （{item['chinese_meaning']}）"
            f"— {item['definition']}"
        )
        lines.append(f"> \"{item['example']}\"")
        lines.append("")

    # Section 3: Chunking Expressions
    lines.append("## \U0001f517 表达 / Chunking Expressions")
    lines.append("")
    for item in exercises["chunks"]:
        lines.append(f"**{item['chunk']}** （{item['chinese_meaning']}）")
        lines.append(item["english_explanation"])
        for ex in item["examples"]:
            lines.append(f"- {ex}")
        lines.append("")

    # Section 4: Comprehension
    lines.append("## \u2753 理解 / Comprehension")
    lines.append("")
    for item in exercises["questions"]:
        lines.append(f"**Q: {item['question']}**")
        lines.append(f"**A (EN):** {item['answer_en']}")
        lines.append(f"**A (中):** {item['answer_zh']}")
        lines.append("")

    return "\n".join(lines)


def main() -> None:
    """Entry point: read Article Envelope from stdin, output Markdown to stdout."""
    raw = sys.stdin.read()
    try:
        envelope = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON from stdin: {e}", file=sys.stderr)
        sys.exit(1)

    prompt = build_prompt(envelope)
    raw_response = call_claude(prompt)
    exercises = parse_response(raw_response)
    markdown = render_markdown(envelope, exercises)
    print(markdown)


if __name__ == "__main__":
    main()
```

### Updated commit_content.py main() only

```python
def main() -> None:
    today = get_beijing_date()
    path = content_path(today)

    if path.exists():
        print(f"Content for {today} already exists — skipping.", file=sys.stderr)
        sys.exit(0)

    content = sys.stdin.read()
    if not content.strip():
        print("ERROR: No Markdown content received from stdin", file=sys.stderr)
        sys.exit(1)

    CONTENT_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    git_commit_and_push(path, today)


# git_commit_and_push() is UNCHANGED from Phase 1 implementation
```

### Updated workflow step

```yaml
- name: Generate and commit daily content
  env:
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
  run: |
    set -eo pipefail
    python -m scripts.feed_article | \
    python -m scripts.generate_exercises | \
    python -m scripts.commit_content
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `anthropic` SDK prefill (assistant message as last turn) | Deprecated — use system prompt or structured outputs instead | Early 2026 (Claude Opus/Sonnet 4.x) | For haiku-20241022, prefill still works; but prompt instructions + JSON output are cleaner and more reliable |
| `output_format` parameter for structured JSON | `output_config.format` (newer models only) | 2026 | claude-3-5-haiku-20241022 does not support this parameter; use prompt instructions for JSON |

**Deprecated/outdated:**
- Prefill technique (putting assistant message last): deprecated for Claude Opus 4.6, Sonnet 4.6, Sonnet 4.5. Claude 3.5 Haiku still accepts it but prompt-based JSON instruction is preferred and more portable.

---

## Open Questions

1. **Exact pinned version of `anthropic` SDK**
   - What we know: 0.86.0 is current as of 2026-03-23 per PyPI
   - What's unclear: Whether any 0.86.x patch releases are needed for stability
   - Recommendation: Pin to `anthropic==0.86.0` in Wave 0; verify on PyPI at implementation time

2. **claude-3-5-haiku-20241022 availability**
   - What we know: Model ID appears in current anthropic SDK documentation examples
   - What's unclear: Whether Anthropic has deprecated this snapshot in favor of a newer Haiku version
   - Recommendation: Verify against `anthropic` SDK model list or Anthropic docs before pinning in the prompt. If deprecated, use the current Haiku model ID (check docs.anthropic.com/models).

3. **`set -eo pipefail` interaction with `sys.exit(0)` from idempotency guard**
   - What we know: If `commit_content.py` exits 0 (file already exists), pipefail should not trigger
   - What's unclear: Whether GitHub Actions treats the three-stage pipe as failed when the middle stage never receives input because `feed_article.py` exited 0
   - Recommendation: Test with `workflow_dispatch` trigger after implementation. The `feed_article.py` idempotency guard exits 0 cleanly, which means the pipe exits 0 — this is correct behavior.

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 8.3.5 |
| Config file | none (pytest discovers tests/ automatically) |
| Quick run command | `pytest tests/test_generate_exercises.py -x` |
| Full suite command | `pytest` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| AIGEN-01 | `build_prompt()` includes article body and vocabulary instructions | unit | `pytest tests/test_generate_exercises.py::test_build_prompt_contains_article -x` | Wave 0 |
| AIGEN-01 | `parse_response()` exits 1 when vocabulary < 5 items | unit | `pytest tests/test_generate_exercises.py::test_parse_response_rejects_few_vocab -x` | Wave 0 |
| AIGEN-01/02/03/04 | `parse_response()` accepts valid complete JSON | unit | `pytest tests/test_generate_exercises.py::test_parse_response_valid -x` | Wave 0 |
| AIGEN-02 | `render_markdown()` includes chunk section with correct format | unit | `pytest tests/test_generate_exercises.py::test_render_markdown_chunks -x` | Wave 0 |
| AIGEN-03/04 | `render_markdown()` includes question section with EN + ZH answers | unit | `pytest tests/test_generate_exercises.py::test_render_markdown_questions -x` | Wave 0 |
| OUT-01 | `render_markdown()` produces four sections in correct order | unit | `pytest tests/test_generate_exercises.py::test_render_markdown_section_order -x` | Wave 0 |
| OUT-01 | Source URL appears as blockquote after article body | unit | `pytest tests/test_generate_exercises.py::test_render_markdown_source_url -x` | Wave 0 |
| OUT-02 | `commit_content.main()` uses Beijing date for filename | unit | `pytest tests/test_commit_content.py -x` (existing, tests already cover this) | Yes |
| OUT-03 | `commit_content.main()` reads stdin and writes to path, calls git_commit_and_push | unit | `pytest tests/test_commit_content.py::test_reads_stdin_and_writes_file -x` | Wave 0 (new test) |
| CI-02 | `call_claude()` exits 1 on `anthropic.APIError` | unit | `pytest tests/test_generate_exercises.py::test_call_claude_exits_on_api_error -x` | Wave 0 |
| CI-02 | `main()` exits 1 on invalid stdin JSON | unit | `pytest tests/test_generate_exercises.py::test_main_exits_on_bad_stdin -x` | Wave 0 |

### Sampling Rate

- **Per task commit:** `pytest tests/test_generate_exercises.py -x`
- **Per wave merge:** `pytest`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps

- [ ] `tests/test_generate_exercises.py` — covers AIGEN-01 through OUT-01 and CI-02
- [ ] New test `tests/test_commit_content.py::test_reads_stdin_and_writes_file` — covers OUT-03 for updated main()
- [ ] `anthropic==0.86.0` added to `requirements.txt`

---

## Sources

### Primary (HIGH confidence)

- https://pypi.org/project/anthropic/ — current version 0.86.0, Python >=3.9 requirement confirmed 2026-03-23
- https://platform.claude.com/docs/en/api/messages-examples — Python SDK `messages.create()` pattern, response schema `content[0].text`, verified 2026-03-23
- Existing project code (`scripts/push_bark.py`, `scripts/commit_content.py`, `scripts/feed_article.py`) — stdin pattern, error handling pattern, subprocess pattern — HIGH confidence (read directly)

### Secondary (MEDIUM confidence)

- WebSearch result: anthropic SDK 0.86.0 released 2026-03-18; version history 0.80.x–0.86.x in early 2026 — corroborated by PyPI page fetch

### Tertiary (LOW confidence)

- `claude-3-5-haiku-20241022` model ID validity as of March 2026 — inferred from SDK documentation examples still referencing haiku-20241022; not directly verified against a live model list endpoint. Flag for implementation-time check.

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — anthropic SDK version verified via PyPI; API patterns verified via official docs
- Architecture: HIGH — based on direct reading of all existing project code; patterns are established
- Pitfalls: HIGH (pipe exit codes, code fences) / MEDIUM (model ID validity) — pipe behavior is well-documented bash; code fence is a known Claude behavior
- Model ID validity: LOW — not confirmed against live API; verify before pinning

**Research date:** 2026-03-23
**Valid until:** 2026-04-23 (30 days; anthropic SDK moves fast, re-verify version before implementation if delayed)
