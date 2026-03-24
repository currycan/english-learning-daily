---
status: testing
phase: 01-claude-openai-api-key-gemini-api
source: [01-01-SUMMARY.md, 01-02-SUMMARY.md]
started: 2026-03-24T06:30:00Z
updated: 2026-03-24T06:30:00Z
---

## Current Test

number: 2
name: No old provider references in production files
expected: |
  Run `grep -r "anthropic\|openai\|call_ai\|call_claude\|resolve_provider\|ANTHROPIC_API_KEY\|OPENAI_API_KEY" scripts/ plan/config.json .github/workflows/`.
  Should return zero matches.
awaiting: user response

## Tests

### 1. Test suite passes with Gemini-only code
expected: Run `pytest` from the project root (with venv active). All 114 tests pass with 0 failures. No imports of anthropic or openai should exist.
result: pass

### 2. No old provider references in production files
expected: Run `grep -r "anthropic\|openai\|call_ai\|call_claude\|resolve_provider\|ANTHROPIC_API_KEY\|OPENAI_API_KEY" scripts/ plan/config.json .github/workflows/`. Should return zero matches (only negative-assertion test lines in tests/ are OK).
result: [pending]

### 3. Config has correct Gemini model
expected: Open `plan/config.json`. It should contain `"gemini_model": "gemini-2.5-flash-lite"` and NOT contain `ai_provider`, `openai_model`, `claude_model`, `anthropic_base_url`, or `anthropic_auth_token`.
result: [pending]

### 4. CI workflow uses only GEMINI_API_KEY
expected: Open `.github/workflows/daily-content.yml`. The env block in the "Generate and commit daily content" step should contain exactly `GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}` and no references to `ANTHROPIC_API_KEY`, `ANTHROPIC_BASE_URL`, `ANTHROPIC_AUTH_TOKEN`, or `OPENAI_API_KEY`.
result: [pending]

### 5. Local content preview generates output
expected: Set `GEMINI_API_KEY` in your environment, then run `python -m scripts.generate_task` from the project root. Should print a JSON payload with `title`, `body`, and `url` fields — no errors, no "ERROR:" lines on stderr. (Skip if you don't have a Gemini API key handy.)
result: [pending]

## Summary

total: 5
passed: 1
issues: 0
pending: 4
skipped: 0
blocked: 0

## Gaps

[none yet]
