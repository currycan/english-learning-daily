---
phase: 3
slug: ai-pipeline
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-23
---

# Phase 3 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x |
| **Config file** | `pytest.ini` / `pyproject.toml` (project root) |
| **Quick run command** | `pytest tests/test_generate_exercises.py -x -q` |
| **Full suite command** | `pytest -x -q` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/test_generate_exercises.py -x -q`
- **After every plan wave:** Run `pytest -x -q`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 3-01-01 | 01 | 0 | AIGEN-01 | unit | `pytest tests/test_generate_exercises.py::test_build_prompt -x -q` | ❌ W0 | ⬜ pending |
| 3-01-02 | 01 | 1 | AIGEN-02 | unit | `pytest tests/test_generate_exercises.py::test_parse_response -x -q` | ❌ W0 | ⬜ pending |
| 3-01-03 | 01 | 1 | AIGEN-03 | unit | `pytest tests/test_generate_exercises.py::test_parse_response_strips_fences -x -q` | ❌ W0 | ⬜ pending |
| 3-01-04 | 01 | 1 | AIGEN-04 | unit | `pytest tests/test_generate_exercises.py::test_render_markdown -x -q` | ❌ W0 | ⬜ pending |
| 3-02-01 | 02 | 2 | OUT-01 | integration | `pytest tests/test_commit_content.py::test_main_writes_file -x -q` | ❌ W0 | ⬜ pending |
| 3-02-02 | 02 | 2 | OUT-02 | integration | `pytest tests/test_commit_content.py::test_main_git_commit -x -q` | ❌ W0 | ⬜ pending |
| 3-02-03 | 02 | 2 | OUT-03 | integration | `pytest tests/test_commit_content.py::test_pipeline_exit_on_api_failure -x -q` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_generate_exercises.py` — stubs for AIGEN-01~04 (prompt building, response parsing, fence stripping, markdown rendering)
- [ ] `tests/test_commit_content.py` — stubs for OUT-01~03 (file write, git commit, pipeline exit behavior)
- [ ] `anthropic>=0.86.0` added to `requirements.txt`

*Existing `conftest.py` and `pytest` infrastructure assumed present from prior phases.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| `content/YYYY-MM-DD.md` committed and pushed to remote | OUT-01 | Requires live git remote + real GitHub Actions run | Run `workflow_dispatch` on `daily-content.yml`; verify file appears in repo |
| Inferential question present in output | AIGEN-04 | Subjective content quality | Inspect generated file; confirm at least one question requires inference, not recall |
| `set -eo pipefail` propagates intermediate pipe failure | OUT-03 | Requires end-to-end CI environment | Introduce deliberate API failure; confirm GitHub Actions job fails, no partial file committed |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
