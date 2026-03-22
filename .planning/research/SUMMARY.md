# Project Research Summary

**Project:** English Daily Content — automated article fetch + AI exercise generation
**Domain:** RSS-to-AI content pipeline with GitHub Actions and git-committed Markdown output
**Researched:** 2026-03-22
**Confidence:** MEDIUM

## Executive Summary

This project adds an automated daily English learning content pipeline to an existing GitHub Actions-driven study system. The pattern is straightforward: fetch one real article from VOA Learning English RSS, pass it through a single Claude API call to extract vocabulary and comprehension questions, render the result as Markdown, and commit it to `content/YYYY-MM-DD.md`. The existing codebase already establishes the exact architecture to follow — a Unix pipeline of single-concern Python scripts communicating via stdout/stdin JSON envelopes. The new system is a direct extension of that pattern, adding two new stages (RSS fetch, Claude API) and replacing the Bark notification delivery stage with a git commit stage.

The recommended approach is to build four scripts (`fetch_article.py`, `generate_exercises.py`, `render_markdown.py`, `commit_content.py`) plus a shared utilities module, wired together in a new GitHub Actions workflow using `|` pipes. The stack additions are minimal: `feedparser` for robust RSS parsing and the `anthropic` SDK for the Claude API call. Using `claude-haiku-3-5` keeps daily API cost near zero. VOA Special English as the primary source eliminates most B1-B2 level-filtering complexity because that source is already calibrated for non-native learners.

The key risks are operational, not architectural: GitHub Actions scheduled workflows are not guaranteed to fire on free-tier repos; RSS feed structure changes without warning; and committing from CI requires explicit write permissions and git identity configuration. All three are well-understood problems with established mitigations. The timezone date mismatch pitfall (UTC runner vs. Beijing local time) is subtle and often missed — it must be addressed explicitly in the date-derivation logic. Build in a tight order (utilities first, then each pipeline stage, workflow last) and the dependency chain is clean throughout.

## Key Findings

### Recommended Stack

The existing stack is extended with exactly two new libraries. All other functionality uses the Python stdlib or dependencies already pinned in `requirements.txt`. This is the correct call: the pipeline makes one HTTP call and one AI call per day from CI — there is no async requirement, no multi-template complexity, and no justification for additional dependencies.

**Core technologies:**
- `Python 3.12` (CI): all script logic — already the project runtime; no second language
- `feedparser 6.0.11`: RSS parsing — handles malformed XML, encoding quirks, and CDATA blocks that `xml.etree` cannot survive
- `anthropic >=0.25.0,<1.0`: Claude API client — official SDK with built-in auth, retry, and typed responses
- `claude-haiku-3-5`: AI model — 3x cheaper than Sonnet; sufficient for structured vocabulary/question extraction at ~1,400 tokens/day
- `requests 2.32.3` (existing): HTTP fetching — already pinned; no async overhead needed for one daily call
- `pytest 8.3.5` (existing): test framework — already in use; no change
- `subprocess` + git CLI: CI commits — already the project pattern from `mark_done.py`
- stdlib only (`pathlib`, `textwrap`, `re`, `json`): file I/O, Markdown formatting, level heuristics — no Jinja2, no readability library

**Critical version note:** Pin `anthropic` to an exact version at implementation time (verify current release on PyPI; training knowledge gives 0.25+). The SDK has had breaking shape changes across minor versions.

### Expected Features

The pipeline delivers a daily Markdown file with a fixed structure: article header with source URL, vocabulary section (5-8 words with plain-English definitions and in-article example sentences), comprehension questions (3-5, at least one inferential), and an answer key. This is the complete v1 scope.

**Must have (table stakes):**
- Real article content fetched from VOA/BBC RSS — authentic input is non-negotiable for language acquisition
- Correct B1-B2 level calibration — VOA Special English handles this at source; minimal extra filtering needed
- Vocabulary highlights (5-8 words) with plain-English definitions and in-article example sentences
- Comprehension questions (3-5) including at least one inferential question, with answers
- Consistent daily availability — the whole value proposition depends on reliability
- Idempotent output — running twice on the same day must not overwrite or duplicate
- Graceful source failure handling — exit non-zero on failure so Actions marks the job failed; fallback to BBC before giving up
- Readable Markdown with consistent heading structure for grep/search across weeks

**Should have (differentiators):**
- Source URL in file header — connects learning content to the real article
- Inferential comprehension questions explicitly required in prompt — most generators default to factual only
- Article topic tag (single metadata line) — enables future filtering by domain once the archive grows
- CEFR level label on each vocabulary word (B1/B2) — gives learner a mental model of their progress boundary

**Defer (v2+):**
- Vocabulary reuse detection (skip already-taught words) — high complexity, zero value before 30 days of data; revisit at Week 8+
- B1-B2 word classification labels requiring CEFR wordlist — defer until core pipeline is stable; accuracy is approximate anyway
- Audio/TTS generation — binary assets in git, extra API cost, separate infra concern
- Interactive exercises — incompatible with static Markdown output model

### Architecture Approach

The new pipeline is a direct extension of the existing `generate_task.py | push_bark.py` architecture: discrete single-concern scripts communicate via stdout/stdin JSON envelopes. Each stage is independently testable by piping fixture JSON to it. The GitHub Actions workflow wires stages with `|` pipes and provides secrets as environment variables. No shared mutable state crosses component boundaries; the filesystem (`content/YYYY-MM-DD.md` existence) is the only idempotency mechanism.

**Major components:**
1. `scripts/content_utils.py` — shared pure functions (date helpers, level-scoring heuristic, idempotency check); no I/O; required by all other scripts
2. `scripts/fetch_article.py` — fetch VOA RSS (with BBC fallback), select one item, validate minimum length, emit Article Envelope JSON to stdout
3. `scripts/generate_exercises.py` — read Article Envelope from stdin, call Claude API once (single structured JSON prompt), emit Content Envelope JSON to stdout
4. `scripts/render_markdown.py` — read Content Envelope from stdin, apply pure formatting function, emit Markdown string to stdout
5. `scripts/commit_content.py` — read Markdown string from stdin, check idempotency, write file, git add/commit/push; exit 0 if already committed, exit 1 on any error
6. `.github/workflows/content.yml` — cron workflow wiring all four stages with `|` pipes; sets `permissions: contents: write`

**Data flow:** Article Envelope (JSON) → Content Envelope (JSON) → Markdown string → committed file

### Critical Pitfalls

1. **GitHub Actions scheduled workflows are not guaranteed to run** — keep `workflow_dispatch` always enabled for manual recovery; add an `if: failure()` Bark notification step so silent skips surface as alerts; keep the repo active to avoid deprioritization
2. **RSS feed structure changes without warning** — use `feedparser` (not `xml.etree`); validate extracted body length >= 200 chars before calling Claude; log raw feed item on first use
3. **Committing from CI requires explicit write permissions and git identity** — add `permissions: contents: write` to the workflow job; set `git config user.name` and `user.email` before committing; push with `git push origin HEAD:master` explicitly
4. **Claude API produces inconsistent output structure without strict format constraints** — require JSON output in the prompt with explicit schema; parse with `json.loads()` in Python and validate structure; pin a specific model version (e.g. `claude-3-5-haiku-20241022`) not a floating alias
5. **UTC runner date vs. Beijing local date mismatch** — derive target date with explicit timezone: `TZ='Asia/Shanghai' date +%Y-%m-%d` in the workflow or `datetime.now(ZoneInfo("Asia/Shanghai")).date()` in Python; document the convention as a constant; never rely on implicit system clock

## Implications for Roadmap

Based on research, the dependency chain is clear and the build order is dictated by it. Three phases cover the complete scope.

### Phase 1: Foundation and Infrastructure

**Rationale:** Pipeline stages cannot be tested or integrated until shared utilities exist and the CI environment is verified to support git commits. Timezone, permissions, and idempotency logic must be established before any content logic is written — these are the failure modes that cause silent data loss.
**Delivers:** `content_utils.py` with shared helpers; `content/` directory initialized with `.gitkeep`; CI workflow skeleton with correct `permissions: contents: write`, git identity, and timezone-aware date derivation; `commit_content.py` with idempotency check; verified git commit/push from Actions
**Addresses:** Idempotent output, consistent daily availability (table stakes)
**Avoids:** Pitfalls 3 (CI write permissions), 5 (timezone date mismatch), 11 (missing `content/` directory)
**Research flag:** Standard patterns — well-documented GitHub Actions configuration; no phase research needed

### Phase 2: RSS Fetch and Article Pipeline

**Rationale:** The fetch stage is the entry point of the pipeline. It must be stable and validated with real feed data before the AI stage is built on top of it. Feed fragility (Pitfall 2) and User-Agent blocking (Pitfall 6) must be hardened here, not discovered during AI integration.
**Delivers:** `fetch_article.py` with VOA primary source, BBC fallback, minimum length validation, User-Agent header, and plain-text body extraction; fixture JSON for testing downstream stages; integration with `commit_content.py` end-to-end without AI
**Uses:** `feedparser 6.0.11`, `requests 2.32.3` (existing)
**Implements:** Article Envelope schema; graceful source failure handling
**Addresses:** Real article content, graceful source failure handling, readable Markdown output (table stakes)
**Avoids:** Pitfalls 2 (RSS structure change), 6 (User-Agent blocking), 8 (duplicate-skip logic — check before fetch)
**Research flag:** Needs validation — verify live VOA and BBC RSS feed URLs and field names before coding the parser; `feedparser` field names differ from `xml.etree` and change across feed versions

### Phase 3: AI Exercise Generation and Markdown Rendering

**Rationale:** The AI stage depends on a stable Article Envelope from Phase 2. Building it last means the prompt can be tested against real article content rather than synthetic fixtures. Markdown rendering is a pure function with no external dependencies — easiest to complete once the data model is locked.
**Delivers:** `generate_exercises.py` with single Claude API call, structured JSON prompt, response validation; `render_markdown.py` as pure formatting function; complete end-to-end pipeline from RSS to committed Markdown file; failure notification step in workflow
**Uses:** `anthropic >=0.25.0,<1.0`, `claude-3-5-haiku-20241022` (pinned model)
**Implements:** Content Envelope schema; vocabulary highlights (5-8 words), comprehension questions (3-5, at least one inferential), answer key, source URL header
**Addresses:** All remaining table stakes features; inferential questions and source attribution differentiators
**Avoids:** Pitfalls 4 (inconsistent Claude output structure), 7 (retry cost overrun — try-once policy), 9 (unpinned anthropic SDK), 10 (non-ASCII encoding)
**Research flag:** Needs validation — verify current `anthropic` SDK version on PyPI; verify `claude-3-5-haiku-20241022` model ID against Anthropic docs; test JSON output mode prompt pattern against actual SDK response shape before writing parser

### Phase Ordering Rationale

- Phase 1 first because timezone, permissions, and idempotency bugs cause silent data loss — these must be known-good before content logic is layered on
- Phase 2 before Phase 3 because the Article Envelope JSON schema is the contract between the two stages; defining it through real feed data produces a more accurate schema than a synthetic one
- Phase 3 last because it has the most external dependencies (Anthropic SDK, live model behavior) and benefits from all earlier work being stable
- Each phase produces a verifiable artifact that can be committed and tested independently

### Research Flags

Needs deeper research during planning:
- **Phase 2:** Verify live VOA and BBC RSS feed URLs, field names, and CDATA patterns — feed structure is the most fragile external dependency
- **Phase 3:** Verify current `anthropic` Python SDK version; verify `claude-3-5-haiku-20241022` model ID; test JSON structured output prompt format against actual SDK behavior

Standard patterns (skip research-phase):
- **Phase 1:** GitHub Actions `permissions: contents: write`, git identity in CI, and timezone handling are well-documented patterns with no ambiguity
- **Phase 1:** `content_utils.py` pure functions follow the same shape as existing `plan_state.py` — no research needed

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | MEDIUM | Core choices (Python, requests, pytest) are HIGH — already pinned in project. `feedparser` version and `anthropic` SDK version need PyPI verification at implementation time. Claude model ID needs Anthropic docs verification. |
| Features | MEDIUM | Table stakes are grounded in established SLA research (CEFR, Nation, Krashen). Prioritization reflects project constraints and is inherently subjective. Vocabulary reuse detection complexity assessment is HIGH confidence. |
| Architecture | HIGH | Existing codebase establishes the exact pattern. New pipeline is a direct extension. Component boundaries, envelope schemas, and build order are all determined by existing code, not inference. |
| Pitfalls | MEDIUM | Structural pitfalls (CI permissions, timezone, idempotency, feed fragility) are HIGH confidence. SDK version specifics (Pitfall 9 exact version number) are MEDIUM — verify at implementation time. |

**Overall confidence:** MEDIUM-HIGH

### Gaps to Address

- **`feedparser` vs `xml.etree` for RSS:** STACK.md recommends `feedparser`; ARCHITECTURE.md Component Detail for `fetch_article.py` mentions `xml.etree.ElementTree` as an alternative (without `feedparser`). PITFALLS.md strongly recommends `feedparser`. Resolve: use `feedparser`. The ARCHITECTURE.md mention of `xml.etree` should be treated as a draft note, not a recommendation.
- **Anthropic SDK exact version:** Cannot be verified without web access. Flag for developer to check `pip index versions anthropic` before pinning in requirements.txt.
- **Claude model ID:** `claude-3-5-haiku-20241022` is the training-data name. Verify against Anthropic model docs at implementation time — model IDs have changed in past releases.
- **VOA RSS feed URL stability:** VOA has reorganized feed URLs in the past. Verify the current URL structure before coding the fetcher. Store in `plan/config.json`, not hardcoded.
- **CEFR word classification accuracy:** Marking vocabulary as B1/B2 with Claude is approximate (no wordlist lookup). Acceptable for a personal tool; document the limitation in the prompt so the learner has correct expectations.

## Sources

### Primary (HIGH confidence)
- Existing codebase analysis: `scripts/plan_state.py`, `scripts/push_bark.py`, `scripts/mark_done.py` — architecture pattern
- Existing workflow: `.github/workflows/morning.yml` — CI pattern, Python version, action versions
- Existing `requirements.txt`: `requests==2.32.3`, `pytest==8.3.5`, `pytest-cov==7.0.0` — stack baseline
- `.planning/PROJECT.md` — constraints: one call/day, minimal cost, no new runtime beyond requests + anthropic
- `.planning/codebase/ARCHITECTURE.md` — existing component inventory

### Secondary (MEDIUM confidence)
- CEFR framework (Council of Europe) — feature level calibration rationale
- Nation (2001) "Learning Vocabulary in Another Language" — vocabulary highlight feature rationale
- Krashen comprehensible input hypothesis — authentic article requirement rationale
- Training knowledge (August 2025 cutoff): `feedparser` 6.x stable, Anthropic SDK 0.25+, GitHub Actions scheduler behavior, git-from-CI patterns

### Tertiary (LOW confidence — verify at implementation)
- `feedparser==6.0.11` exact version — needs PyPI verification
- `anthropic>=0.25.0,<1.0` version range — needs PyPI verification for current release
- `claude-3-5-haiku-20241022` model ID — needs Anthropic docs verification
- VOA Learning English RSS URL — needs live verification before coding

---
*Research completed: 2026-03-22*
*Ready for roadmap: yes*
