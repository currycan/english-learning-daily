---
phase: 1
slug: foundation
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-22
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.3.5 |
| **Config file** | `pytest.ini` (exists — sets `pythonpath = .`) |
| **Quick run command** | `pytest tests/test_content_utils.py tests/test_commit_content.py -x` |
| **Full suite command** | `pytest` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/test_content_utils.py tests/test_commit_content.py -x`
- **After every plan wave:** Run `pytest`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 1-01-01 | 01 | 0 | CI-01 | unit | `pytest tests/test_content_utils.py -x` | ❌ W0 | ⬜ pending |
| 1-01-02 | 01 | 0 | CI-01, CI-02 | unit | `pytest tests/test_commit_content.py -x` | ❌ W0 | ⬜ pending |
| 1-01-03 | 01 | 1 | CI-01 | unit | `pytest tests/test_content_utils.py -x` | ✅ after W0 | ⬜ pending |
| 1-01-04 | 01 | 1 | CI-01, CI-02 | unit | `pytest tests/test_commit_content.py -x` | ✅ after W0 | ⬜ pending |
| 1-01-05 | 01 | 1 | CI-01 | manual | Run `workflow_dispatch`; observe green CI and `content/YYYY-MM-DD.md` committed | N/A | ⬜ pending |
| 1-01-06 | 01 | 2 | CI-01 | manual | Run `workflow_dispatch` twice same day; second run exits 0, no duplicate commit | N/A | ⬜ pending |
| 1-01-07 | 01 | 2 | CI-02 | manual | Run `workflow_dispatch` with script that exits 1; observe red CI | N/A | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_content_utils.py` — stubs for `get_beijing_date()`, `content_path()` (CI-01)
- [ ] `tests/test_commit_content.py` — stubs for idempotency guard and git failure exit (CI-01, CI-02)

*Existing infrastructure covers all framework needs — `pytest.ini` present, `pytest 8.3.5` in `requirements.txt`.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Workflow cron fires at 22:00 UTC and commits file with correct Beijing date | CI-01 | Cannot mock GitHub Actions cron in unit tests | Trigger `workflow_dispatch`; verify `content/YYYY-MM-DD.md` filename uses BJT date (one day ahead of UTC at 22:xx UTC) |
| Re-run on same day produces no duplicate commit | CI-01 | Requires live git state on GitHub | Run `workflow_dispatch` twice same day; second run must exit 0 with "already exists" log and no new commit in git history |
| Non-zero script exit marks CI job red | CI-02 | Requires live GitHub Actions environment | Temporarily modify `commit_content.py` to `sys.exit(1)`; trigger `workflow_dispatch`; verify job shows red ✗ in Actions UI |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
