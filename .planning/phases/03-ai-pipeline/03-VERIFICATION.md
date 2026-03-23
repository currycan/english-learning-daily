---
phase: 03-ai-pipeline
verified: 2026-03-23T02:30:00Z
status: passed
score: 7/7 must-haves verified
re_verification: false
---

# Phase 3: AI Pipeline Verification Report

**Phase Goal:** Every day a complete English lesson Markdown file is committed to `content/YYYY-MM-DD.md` — containing the real article, 5-8 vocabulary entries, chunking expressions, and comprehension questions with answers
**Verified:** 2026-03-23
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (derived from Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|---------|
| 1 | Full three-stage pipeline exists and is wired in CI workflow: feed_article \| generate_exercises \| commit_content | VERIFIED | `.github/workflows/daily-content.yml` lines 34-36; all three module references confirmed |
| 2 | Committed file contains four clearly separated sections: article text + source URL, vocabulary (5-8), chunking expressions, comprehension Q&A | VERIFIED | `render_markdown()` in `scripts/generate_exercises.py` produces all four emoji-headed sections in correct order; 4 section-order tests pass |
| 3 | Comprehension section contains at least one inferential question (prompt enforces this) | VERIFIED | `build_prompt()` contains "At least ONE question must be inferential (requiring reasoning or inference)"; `test_build_prompt_inferential_instruction` confirms "inferential" present in prompt |
| 4 | If the Claude API call fails, the pipeline exits non-zero and no partial file is committed | VERIFIED | `call_claude()` catches Exception and calls `sys.exit(1)` before any write; `test_call_claude_exits_on_api_error` passes; `set -eo pipefail` in workflow propagates failures |
| 5 | commit_content.py reads real Markdown from stdin, not a placeholder | VERIFIED | `scripts/commit_content.py` line 30: `content = sys.stdin.read()`; placeholder text gone; `test_reads_stdin_and_writes_file` passes |
| 6 | Idempotency guard still exits 0 when today's file already exists | VERIFIED | `commit_content.py` lines 26-28 check `path.exists()` and `sys.exit(0)`; `test_skips_when_file_exists` passes |
| 7 | All 90 tests pass — no regressions | VERIFIED | Full suite: `90 passed in 0.27s` |

**Score:** 7/7 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `requirements.txt` | Contains `anthropic==0.86.0` | VERIFIED | Line 4: `anthropic==0.86.0`; existing deps preserved |
| `scripts/generate_exercises.py` | 5 exports: build_prompt, call_claude, parse_response, render_markdown, main; 148 lines | VERIFIED | 148 lines; all 5 functions present; `MODEL = "claude-3-5-haiku-20241022"` pinned; importable |
| `tests/test_generate_exercises.py` | 12 test functions; all passing | VERIFIED | 12 tests counted via `grep -c`; all 12 PASSED in test run |
| `scripts/commit_content.py` | main() reads stdin; no placeholder; git_commit_and_push unchanged | VERIFIED | `sys.stdin.read()` at line 30; "placeholder" absent from file; `git_commit_and_push` unchanged |
| `tests/test_commit_content.py` | test_reads_stdin_and_writes_file passing GREEN | VERIFIED | 5 tests all PASSED including the new stdin test |
| `.github/workflows/daily-content.yml` | Three-stage pipe; set -eo pipefail; ANTHROPIC_API_KEY env block | VERIFIED | All three verified at lines 31-36; step named "Generate and commit daily content" |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `tests/test_generate_exercises.py` | `scripts/generate_exercises.py` | `import scripts.generate_exercises as ge` | WIRED | Line 7; all 12 tests exercise real implementation |
| `tests/test_commit_content.py` | `scripts/commit_content.py` | `import scripts.commit_content as cc` | WIRED | Line 9; test_reads_stdin_and_writes_file exercises new main() |
| `scripts/generate_exercises.py` | `anthropic.Anthropic` | `client = anthropic.Anthropic()` inside `call_claude()` | WIRED | Line 47; created inside function enabling clean test patching |
| `scripts/generate_exercises.py` | `sys.stdin` | `sys.stdin.read()` in `main()` | WIRED | Line 132 |
| `scripts/generate_exercises.py` | `sys.stdout` | `print(markdown)` in `main()` | WIRED | Line 143 |
| `.github/workflows/daily-content.yml` | `scripts/generate_exercises.py` | `python -m scripts.generate_exercises` (middle stage) | WIRED | Line 35 |
| `.github/workflows/daily-content.yml` | `scripts/commit_content.py` | `python -m scripts.commit_content` (final stage) | WIRED | Line 36 |
| `scripts/commit_content.py` | `scripts/content_utils.py` | `from scripts.content_utils import get_beijing_date, content_path, CONTENT_DIR` | WIRED | Line 6; all three symbols used in `main()` |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|---------|
| AIGEN-01 | 03-01, 03-02 | AI extracts 5-8 key vocabulary words with plain-English definitions and in-article examples | SATISFIED | `parse_response()` enforces `len(vocabulary) >= 5`; `build_prompt()` specifies 5-8 with verbatim examples; test_parse_response_rejects_few_vocab passes |
| AIGEN-02 | 03-01, 03-02 | AI extracts 3-5 chunking expressions with Chinese meaning and 2+ usage examples | SATISFIED | `build_prompt()` specifies chunks array with chinese_meaning and 2 examples; render_markdown formats them; test_render_markdown_chunks passes |
| AIGEN-03 | 03-01, 03-02 | AI generates 3-5 comprehension questions covering factual recall and inference | SATISFIED | `build_prompt()` requires 3-5 questions with at least one inferential; test_build_prompt_inferential_instruction passes |
| AIGEN-04 | 03-01, 03-02 | AI generates answers for all comprehension questions | SATISFIED | Claude API response schema includes answer_en and answer_zh per question; render_markdown emits both; test_render_markdown_questions passes |
| OUT-01 | 03-01, 03-02 | Markdown file with four sections: article + source URL, vocabulary, chunks, comprehension Q&A | SATISFIED | All four emoji-headed sections rendered in correct order; section-order test and source-URL test pass |
| OUT-02 | 03-03 | File named content/YYYY-MM-DD.md using Beijing time (UTC+8) | SATISFIED | `commit_content.py` uses `get_beijing_date()` and `content_path(today)` from `content_utils.py` (Beijing TZ logic in that module, validated in Phase 1) |
| OUT-03 | 03-03 | System commits and pushes rendered file to git via GitHub Actions on each successful run | SATISFIED | `git_commit_and_push()` unchanged and called by new `main()`; workflow runs the full pipe end-to-end |

No orphaned requirements: all 7 declared requirement IDs (AIGEN-01 through AIGEN-04, OUT-01 through OUT-03) are accounted for. REQUIREMENTS.md traceability table confirms Phase 3 owns exactly these 7.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| None | — | — | — | — |

No TODOs, FIXMEs, placeholder strings, empty return stubs, or hardcoded secrets found in any Phase 3 file.

One design note (not a blocker): `call_claude()` catches bare `Exception` rather than `anthropic.APIError` specifically. This was a deliberate decision documented in both 03-01-SUMMARY.md and 03-02-SUMMARY.md: the RED phase test used `Exception("API error")` as the side_effect to avoid APIError init complexity, and the GREEN implementation was written to match. The broad catch does not weaken error propagation — it still exits 1 on any failure — but it does mean non-API errors (e.g., network errors from other sources) are silently categorized as "API errors". This is a minor code-quality observation, not a goal-blocking issue.

### Human Verification Required

#### 1. End-to-end pipeline with live Claude API

**Test:** Set `ANTHROPIC_API_KEY` in environment and run `python -m scripts.feed_article | python -m scripts.generate_exercises | python -m scripts.commit_content` from the repo root.
**Expected:** A file `content/YYYY-MM-DD.md` appears with four sections containing real vocabulary, chunk expressions, and comprehension questions derived from a live VOA article.
**Why human:** Requires a live `ANTHROPIC_API_KEY` and live RSS feed; cannot be verified programmatically in this environment.

#### 2. Inferential question quality in generated output

**Test:** Inspect the comprehension questions section in a real generated `content/*.md` file.
**Expected:** At least one question cannot be answered by simple factual recall — it requires reasoning or drawing an inference from the article.
**Why human:** Prompt instructs Claude to produce inferential questions, but quality of compliance requires human judgment.

#### 3. GitHub Actions workflow run

**Test:** Trigger the workflow manually via `workflow_dispatch` on GitHub after setting the `ANTHROPIC_API_KEY` repository secret.
**Expected:** The "Generate and commit daily content" step completes green, and a new `content/YYYY-MM-DD.md` file appears in the repository.
**Why human:** Requires GitHub repository access and configured secret; CI run behavior cannot be verified programmatically here.

### Gaps Summary

None. All automated checks pass.

---

_Verified: 2026-03-23_
_Verifier: Claude (gsd-verifier)_
