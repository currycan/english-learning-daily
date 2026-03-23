---
phase: 03-ai-pipeline
plan: 01
subsystem: ai-pipeline
tags: [tdd, red-phase, anthropic, testing]
dependency_graph:
  requires: []
  provides: [anthropic-sdk-dep, generate-exercises-test-contracts, commit-content-stdin-test]
  affects: [03-02-PLAN]
tech_stack:
  added: [anthropic==0.86.0]
  patterns: [tdd-red-phase, import-error-as-red-state]
key_files:
  created:
    - tests/test_generate_exercises.py
  modified:
    - requirements.txt
    - tests/test_commit_content.py
decisions:
  - "Pin anthropic==0.86.0 exact version in requirements.txt for reproducible CI"
  - "12 tests use ModuleNotFoundError as RED signal (file doesn't exist yet)"
  - "test_call_claude_exits_on_api_error uses Exception mock to avoid APIError init complexity"
metrics:
  duration_seconds: 106
  completed_date: "2026-03-23"
  tasks_completed: 3
  files_modified: 3
---

# Phase 3 Plan 01: TDD RED Phase — anthropic SDK + generate_exercises test contracts

**One-liner:** Added anthropic==0.86.0 SDK dependency and 12 failing unit tests covering build_prompt, parse_response, render_markdown, and call_claude contracts plus one failing stdin test for commit_content.py.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Add anthropic dependency to requirements.txt | b992d39 | requirements.txt |
| 2 | Write failing tests for generate_exercises.py (RED) | 123a184 | tests/test_generate_exercises.py |
| 3 | Add failing stdin test to test_commit_content.py (RED) | c56a5d7 | tests/test_commit_content.py |

## Verification Results

- `grep "anthropic==0.86.0" requirements.txt` — exits 0
- `grep -c "^def test_" tests/test_generate_exercises.py` — prints 12
- `pytest tests/test_generate_exercises.py` — ModuleNotFoundError (RED confirmed)
- `pytest tests/test_commit_content.py::test_reads_stdin_and_writes_file` — FAILED (RED confirmed)
- `pytest tests/ --ignore=tests/test_generate_exercises.py` — 1 failed, 77 passed (only new RED test fails)

## Decisions Made

1. **Pin anthropic==0.86.0**: Exact version pin for reproducible CI builds per RESEARCH.md.
2. **12 tests / ModuleNotFoundError as RED**: Since scripts/generate_exercises.py does not exist, all 12 tests fail at collection (ImportError). This is the correct TDD RED state.
3. **test_call_claude_exits_on_api_error mock approach**: Used `Exception("API error")` side effect instead of `anthropic.APIError` to avoid complex init requirements in RED state; GREEN implementation will handle `anthropic.APIError` specifically.

## Deviations from Plan

None - plan executed exactly as written.

## Self-Check: PASSED

- tests/test_generate_exercises.py: FOUND
- tests/test_commit_content.py: FOUND (with new test appended)
- requirements.txt: FOUND (contains anthropic==0.86.0)
- Commit b992d39: FOUND
- Commit 123a184: FOUND
- Commit c56a5d7: FOUND
