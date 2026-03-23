# Phase 1: Foundation - Research

**Researched:** 2026-03-22
**Domain:** GitHub Actions CI — file commit, idempotency, Beijing timezone, Python script skeleton
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Cron Schedule**
- Run at `0 22 * * *` UTC (= 06:00 BJT next day)
- Content must be available before 08:30 BJT on weekdays (user's morning study time)
- 06:00 BJT gives a comfortable 2.5-hour buffer before reading time
- Same cron expression for every day (weekday and weekend)

**Re-run / Idempotency**
- If `content/YYYY-MM-DD.md` already exists when the workflow runs, skip all processing and exit 0 cleanly
- No overwrite on re-run — content is stable once committed for the day
- This saves API calls and prevents content churn when debugging with `workflow_dispatch`

**content/ Directory**
- Scripts create `content/` directory automatically with `mkdir -p` if it doesn't exist
- No pre-committed placeholder file or README needed — first real run creates the directory
- `pathlib.Path("content").mkdir(parents=True, exist_ok=True)` — follows existing pattern

**Workflow Structure**
- New workflow file: `.github/workflows/daily-content.yml`
- Follows exact same structure as existing `morning.yml` (checkout → setup-python → pip install → run script)
- Adds `permissions: contents: write` at the job level (missing from existing workflows — must add explicitly)
- Adds git identity config step before commit: `git config user.name "github-actions[bot]"` and `git config user.email "github-actions[bot]@users.noreply.github.com"`
- Uses `GITHUB_TOKEN` (built-in) for push — no PAT needed

**Failure Handling**
- Pipeline exits non-zero (`sys.exit(1)`) on any failure — matches existing codebase convention
- Error messages to stderr — matches existing `print(f"ERROR: ...", file=sys.stderr)` pattern
- CI job marked failed in GitHub Actions when exit code is non-zero

**Shared Utilities Module**
- Create `scripts/content_utils.py` for date derivation and shared helpers
- Key function: `get_beijing_date() -> date` — returns today's date in CST (UTC+8) regardless of runner timezone
- Key function: `content_path(date: date) -> Path` — returns `Path(f"content/{date.isoformat()}.md")`
- Follows existing pattern from `scripts/plan_state.py`: pure functions, type hints, no side effects

### Claude's Discretion
- Exact git commit message format for the daily content commit
- Whether to use a `dry_run` flag in Phase 1 placeholder script for testing
- Exact CI step names and comments in the workflow YAML

### Deferred Ideas (OUT OF SCOPE)
- Morning/evening file structure split for AM/PM study sessions — Phase 3 (Markdown rendering)
- Push notification linking to today's content file — out of scope (user reads git directly)
- Weekend cron override (one hour later) — not implemented; GitHub Actions cron doesn't support conditional schedules; single cron at 22:00 UTC serves all days
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| CI-01 | GitHub Actions workflow runs on a daily cron schedule | Cron syntax `0 22 * * *` UTC confirmed; `workflow_dispatch` added for manual testing |
| CI-02 | Pipeline exits non-zero and marks the CI job failed if RSS fetch or AI generation fails | Phase 1 establishes `sys.exit(1)` skeleton pattern; subsequent phases inherit it |
</phase_requirements>

---

## Summary

Phase 1 builds only the CI skeleton: a new workflow (`daily-content.yml`) that runs at 06:00 BJT, delegates to a placeholder Python script (`scripts/commit_content.py`), and exits cleanly when the day's file already exists. No RSS fetching or AI generation is involved yet.

The project already has a working GitHub Actions + Python pipeline (`morning.yml`, `evening.yml`). Phase 1 follows that structure exactly, adding two critical pieces absent from the existing workflows: `permissions: contents: write` at the job level (required for any git push from the runner) and a git identity configuration step (`git config user.name/email`) before the commit. Without both, the push will silently fail or error.

The Beijing-date utility is the only new algorithmic piece: `datetime.now(tz=timezone(timedelta(hours=8))).date()` computes CST regardless of the Ubuntu runner's UTC clock. All other patterns — `sys.exit(1)` on error, `pathlib.Path` for file I/O, `subprocess` for git operations, pure functions with type hints — are copied verbatim from the existing codebase.

**Primary recommendation:** Mirror `morning.yml` exactly; add `permissions: contents: write` and the git identity config step; write `scripts/content_utils.py` with `get_beijing_date()` and `content_path()`; write `scripts/commit_content.py` as a minimal placeholder that checks for existence, writes a stub file, commits, and pushes.

---

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python stdlib `datetime` | 3.12 (pinned in CI) | Beijing-date derivation via `timezone(timedelta(hours=8))` | No external dependency; already used throughout codebase |
| Python stdlib `pathlib` | 3.12 | File existence check, directory creation, file write | Already the codebase standard for all file I/O |
| Python stdlib `subprocess` | 3.12 | `git add / commit / push` from Python | Same pattern as `mark_done.git_commit_and_push()` |
| `actions/checkout@v4` | v4 | Checkout repo with write access when `permissions: contents: write` is set | Exact version used in all existing workflows |
| `actions/setup-python@v5` | v5 | Install Python 3.12 on runner | Exact version used in all existing workflows |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `pytest` | 8.3.5 (pinned in `requirements.txt`) | Unit tests for `content_utils.py` functions | All new modules require a test file following project convention |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `subprocess` for git | `pygit2` or `GitPython` | Third-party deps not allowed; `subprocess` matches existing code |
| `GITHUB_TOKEN` (built-in) | Personal Access Token (PAT) | PAT requires secret management; `GITHUB_TOKEN` is automatic with `permissions: contents: write` |
| `datetime.now(tz=...)` | `pytz` or `pendulum` | No new deps; stdlib `timezone(timedelta(hours=8))` is sufficient for a fixed offset |

**Installation:** No new packages needed for Phase 1. `requirements.txt` stays unchanged.

---

## Architecture Patterns

### Recommended Project Structure (Phase 1 additions)

```
.github/workflows/
├── morning.yml              # existing — unchanged
├── evening.yml              # existing — unchanged
└── daily-content.yml        # NEW — daily content CI

scripts/
├── plan_state.py            # existing — unchanged
├── mark_done.py             # existing — unchanged
├── generate_task.py         # existing — unchanged
├── check_evening.py         # existing — unchanged
├── push_bark.py             # existing — unchanged
├── content_utils.py         # NEW — get_beijing_date(), content_path()
└── commit_content.py        # NEW — Phase 1 placeholder script

content/                     # NEW — created on first successful run
└── YYYY-MM-DD.md            # auto-generated daily files

tests/
├── test_plan_state.py       # existing
├── test_mark_done.py        # existing
└── test_content_utils.py    # NEW — unit tests for content_utils.py
```

### Pattern 1: Beijing Date Derivation

**What:** Compute today's date in CST (UTC+8) using only stdlib, regardless of runner timezone.

**When to use:** Any script that names a file by "today's Beijing date". Must be called at script startup, before any file-existence check.

**Example:**
```python
# scripts/content_utils.py
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

BEIJING_TZ = timezone(timedelta(hours=8))
CONTENT_DIR = Path("content")


def get_beijing_date() -> date:
    """Return today's date in CST (UTC+8) regardless of runner timezone."""
    return datetime.now(tz=BEIJING_TZ).date()


def content_path(d: date) -> Path:
    """Return the canonical content file path for a given date."""
    return CONTENT_DIR / f"{d.isoformat()}.md"
```

### Pattern 2: Idempotency Guard

**What:** Check whether today's content file already exists before doing any work. Exit 0 cleanly if it does.

**When to use:** Entry point of `commit_content.py`, before any I/O or API calls. Prevents duplicate commits on re-run or `workflow_dispatch`.

**Example:**
```python
# scripts/commit_content.py  (Phase 1 placeholder)
import sys
from pathlib import Path
from scripts.content_utils import get_beijing_date, content_path, CONTENT_DIR


def main() -> None:
    today = get_beijing_date()
    path = content_path(today)

    if path.exists():
        print(f"Content for {today} already exists — skipping.")
        sys.exit(0)

    # Phase 1: write placeholder; later phases replace this block
    CONTENT_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(f"# {today}\n\n_Content placeholder — Phase 1_\n")
    print(f"Wrote placeholder: {path}")

    git_commit_and_push(path, today)


if __name__ == "__main__":
    main()
```

### Pattern 3: GitHub Actions Workflow with Write Permissions

**What:** Workflow that can commit and push files to the repository using the built-in `GITHUB_TOKEN`.

**When to use:** Any workflow that writes back to the repo.

**Example:**
```yaml
# .github/workflows/daily-content.yml
name: Daily content

on:
  schedule:
    - cron: '0 22 * * *'   # 22:00 UTC = 06:00 BJT (UTC+8)
  workflow_dispatch:

jobs:
  generate-content:
    runs-on: ubuntu-latest
    permissions:
      contents: write        # REQUIRED for git push via GITHUB_TOKEN

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Configure git identity
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"

      - name: Commit daily content
        run: python -m scripts.commit_content
```

### Pattern 4: Git Commit from Python Script

**What:** Commit and push a specific file using `subprocess`, matching the existing `mark_done.git_commit_and_push()` pattern.

**When to use:** Any script that must commit a file to git as part of CI execution.

**Example:**
```python
# scripts/commit_content.py
import subprocess
import sys
from datetime import date
from pathlib import Path


def git_commit_and_push(path: Path, today: date) -> None:
    try:
        subprocess.run(["git", "add", str(path)], check=True)
        subprocess.run(
            ["git", "commit", "-m", f"content: add {today.isoformat()}"],
            check=True,
        )
        subprocess.run(["git", "push"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"ERROR: git operation failed: {e}", file=sys.stderr)
        sys.exit(1)
```

### Anti-Patterns to Avoid

- **Missing `permissions: contents: write`:** The `GITHUB_TOKEN` in a GitHub Actions job defaults to read-only since 2023. Without this permission at the job level, `git push` will return HTTP 403 and the job will fail. Add it explicitly — the existing `morning.yml` does NOT have it (it doesn't push), so it is not a reference for this.
- **Missing git identity config:** Without `git config user.name` and `git config user.email`, `git commit` will fail with "Author identity unknown". Must be a workflow step before the Python script runs.
- **Using `date.today()` for Beijing date:** `date.today()` returns the runner's local date (UTC on GitHub-hosted runners). At 22:00–23:59 UTC, this is still "yesterday" in Beijing. Must use `datetime.now(tz=timezone(timedelta(hours=8))).date()`.
- **Storing derived state in a file:** Do not add `current_date` or `last_run_date` to any JSON state file. Derive from clock at runtime — this is the established codebase pattern.
- **Running scripts without `-m` flag:** The `pythonpath = .` in `pytest.ini` and the import style (`from scripts.content_utils import ...`) require running scripts as modules: `python -m scripts.commit_content`. Running `python scripts/commit_content.py` directly breaks relative imports.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Beijing timezone offset | Custom UTC offset math | `timezone(timedelta(hours=8))` from stdlib | Already handles DST-free fixed offset correctly; one line |
| File existence idempotency | Locking files, database flags, state.json fields | `Path.exists()` check at script start | Stateless; the file itself is the idempotency token |
| Git push from CI | Custom GitHub API calls | `subprocess` + `GITHUB_TOKEN` with `permissions: contents: write` | Already the codebase pattern; zero new dependencies |

**Key insight:** The content file path `content/YYYY-MM-DD.md` IS the idempotency key. No lock files or state tracking needed.

---

## Common Pitfalls

### Pitfall 1: `GITHUB_TOKEN` Push Fails Without `permissions: contents: write`

**What goes wrong:** The git push returns HTTP 403 "Permission denied". The CI job fails with an unhelpful error deep in subprocess output.

**Why it happens:** GitHub Actions changed the default `GITHUB_TOKEN` permission to read-only in 2023 for new repositories. The existing `morning.yml` workflow omits this block because it never pushes to the repo — it is not a reference for this.

**How to avoid:** Add `permissions: contents: write` at the job level (not the workflow level — job-level is more precise and follows least-privilege). Confirmed in official GitHub Actions docs: https://docs.github.com/en/actions/using-jobs/assigning-permissions-to-jobs

**Warning signs:** CI log shows `remote: Permission to ... denied to github-actions[bot]` or `error: failed to push some refs`.

### Pitfall 2: Wrong Date When Cron Fires Near Midnight UTC

**What goes wrong:** Cron fires at 22:00 UTC = 06:00 BJT (next calendar day). If the script calls `date.today()`, it returns the UTC date (still "yesterday" from Beijing's perspective). The file is written with yesterday's date name.

**Why it happens:** GitHub-hosted runners run in UTC. `date.today()` uses the system clock without timezone conversion.

**How to avoid:** Always use `datetime.now(tz=timezone(timedelta(hours=8))).date()`. This is exactly what the `get_beijing_date()` utility in `content_utils.py` must implement.

**Warning signs:** Content file for 2026-03-22 gets created instead of 2026-03-23 when the cron fires at 22:00 UTC on March 22.

### Pitfall 3: `git commit` Fails With "nothing to commit"

**What goes wrong:** If the placeholder content is identical on two runs (e.g., idempotency check failed to fire or file was deleted and re-created with identical content), `git commit` returns exit code 1 with "nothing to commit". `subprocess.run(..., check=True)` raises `CalledProcessError` and `sys.exit(1)` fires.

**Why it happens:** The idempotency guard (`path.exists()`) protects the normal re-run case, but edge cases (manual file deletion + re-run before push) can still trigger this.

**How to avoid:** Implement the idempotency check as the very first action in `main()`. Optionally, check `git status --porcelain` output before calling `git commit` and skip silently if there is nothing to stage.

**Warning signs:** CI log shows "nothing to commit, working tree clean" followed by a job failure.

### Pitfall 4: `content/` Directory Not in Git (Empty Directory Problem)

**What goes wrong:** Git does not track empty directories. If `content/` is never committed, the directory doesn't exist on a fresh checkout, and `path.write_text()` raises `FileNotFoundError` if `content/` was not created first.

**Why it happens:** Scripts must create `content/` with `mkdir(parents=True, exist_ok=True)` before writing. The decision is to NOT pre-commit a placeholder — the script creates the directory itself.

**How to avoid:** Always call `CONTENT_DIR.mkdir(parents=True, exist_ok=True)` before `path.write_text()`. This is already in the locked decision — enforce it in the implementation.

**Warning signs:** CI log shows `FileNotFoundError: [Errno 2] No such file or directory: 'content/2026-03-22.md'`.

---

## Code Examples

### Beijing Date Utility (verified pattern)

```python
# scripts/content_utils.py
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

BEIJING_TZ = timezone(timedelta(hours=8))
CONTENT_DIR = Path("content")


def get_beijing_date() -> date:
    """Return today's date in CST (UTC+8) regardless of runner timezone."""
    return datetime.now(tz=BEIJING_TZ).date()


def content_path(d: date) -> Path:
    """Return the canonical content file path for a given date."""
    return CONTENT_DIR / f"{d.isoformat()}.md"
```

### Idempotency Guard (existing-file skip)

```python
today = get_beijing_date()
path = content_path(today)

if path.exists():
    print(f"Content for {today} already exists — skipping.")
    sys.exit(0)
```

### Permissions Block in Workflow YAML

```yaml
jobs:
  generate-content:
    runs-on: ubuntu-latest
    permissions:
      contents: write
```

### Git Identity Config Step

```yaml
- name: Configure git identity
  run: |
    git config user.name "github-actions[bot]"
    git config user.email "github-actions[bot]@users.noreply.github.com"
```

### Git Commit Pattern (mirrors `mark_done.git_commit_and_push()`)

```python
def git_commit_and_push(path: Path, today: date) -> None:
    try:
        subprocess.run(["git", "add", str(path)], check=True)
        subprocess.run(
            ["git", "commit", "-m", f"content: add {today.isoformat()}"],
            check=True,
        )
        subprocess.run(["git", "push"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"ERROR: git operation failed: {e}", file=sys.stderr)
        sys.exit(1)
```

### Test Skeleton (follows `test_mark_done.py` pattern)

```python
# tests/test_content_utils.py
from datetime import date, datetime, timezone, timedelta
from pathlib import Path
import pytest
from scripts.content_utils import get_beijing_date, content_path, CONTENT_DIR


def test_content_path_returns_correct_filename():
    d = date(2026, 3, 22)
    assert content_path(d) == Path("content/2026-03-22.md")


def test_get_beijing_date_returns_date():
    result = get_beijing_date()
    assert isinstance(result, date)


def test_beijing_date_differs_from_utc_near_midnight(monkeypatch):
    """At 22:30 UTC on March 22, Beijing date should be March 23."""
    fixed_utc = datetime(2026, 3, 22, 22, 30, tzinfo=timezone.utc)
    monkeypatch.setattr(
        "scripts.content_utils.datetime",
        type("_dt", (), {"now": staticmethod(lambda tz=None: fixed_utc.astimezone(tz))})(),
    )
    # 22:30 UTC = 06:30 BJT on March 23
    # NOTE: real implementation must be testable via dependency injection or monkeypatch
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| PAT (Personal Access Token) for CI git push | `GITHUB_TOKEN` with `permissions: contents: write` | GitHub 2021+ | No secrets to rotate; built-in token handles push |
| Default `GITHUB_TOKEN` has write access | Default `GITHUB_TOKEN` is read-only for new repos | GitHub 2023 | Must explicitly declare `permissions: contents: write` at job level |
| `pytz` for timezone handling | `datetime.timezone` + `timedelta` (stdlib) | Python 3.2+ | Zero new dependency for fixed UTC offsets |

**Deprecated/outdated:**
- `set-output` workflow command: deprecated in 2022; use `$GITHUB_OUTPUT` env file. Not needed for Phase 1 but worth knowing.
- Pinning `actions/checkout@v2` or `v3`: use `@v4` (current, already in use in this repo).

---

## Open Questions

1. **Commit message format for daily content commits**
   - What we know: Discretion given to Claude; existing pattern uses `chore:` prefix in `mark_done.py`
   - What's unclear: Should the content commit use `chore:`, `feat:`, or a custom `content:` type?
   - Recommendation: Use `content: add YYYY-MM-DD` — a project-specific type that makes content commits easy to filter in git log. Falls under Claude's discretion.

2. **`dry_run` flag for Phase 1 placeholder testing**
   - What we know: Discretion given to Claude; useful for local testing without committing
   - What's unclear: Whether a `--dry-run` flag or a `DRY_RUN` env variable is cleaner
   - Recommendation: Implement as `DRY_RUN=1 python -m scripts.commit_content` environment variable pattern — consistent with how the project reads `BARK_TOKEN`. Skip the git commit/push when set; still write the file.

3. **`git push` behavior when `content/` dir is new (no tracking branch)**
   - What we know: `git push` without arguments requires an upstream tracking branch set
   - What's unclear: Whether `actions/checkout@v4` sets up a tracking branch automatically
   - Recommendation: Use `git push origin HEAD` to be explicit, or rely on `actions/checkout@v4` default which sets `origin` correctly. Verified: `actions/checkout@v4` sets `origin` remote and the checked-out branch tracks it — `git push` works without additional flags. Confidence: HIGH (official action behavior).

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 8.3.5 |
| Config file | `pytest.ini` (exists, sets `pythonpath = .`) |
| Quick run command | `pytest tests/test_content_utils.py -x` |
| Full suite command | `pytest` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| CI-01 | `get_beijing_date()` returns correct CST date, especially when UTC is prior day | unit | `pytest tests/test_content_utils.py::test_beijing_date_differs_from_utc_near_midnight -x` | Wave 0 |
| CI-01 | `content_path(date)` returns `content/YYYY-MM-DD.md` | unit | `pytest tests/test_content_utils.py::test_content_path_returns_correct_filename -x` | Wave 0 |
| CI-01 | Idempotency: `main()` exits 0 when file already exists | unit | `pytest tests/test_commit_content.py::test_skips_when_file_exists -x` | Wave 0 |
| CI-02 | `git_commit_and_push()` calls `sys.exit(1)` on `CalledProcessError` | unit | `pytest tests/test_commit_content.py::test_git_failure_exits_nonzero -x` | Wave 0 |
| CI-02 | Workflow YAML: non-zero exit code from script marks job failed | manual | Run `workflow_dispatch` with a script that exits 1; observe red CI | N/A — manual only |

### Sampling Rate

- **Per task commit:** `pytest tests/test_content_utils.py tests/test_commit_content.py -x`
- **Per wave merge:** `pytest`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps

- [ ] `tests/test_content_utils.py` — covers `get_beijing_date()`, `content_path()` (CI-01)
- [ ] `tests/test_commit_content.py` — covers idempotency guard and git failure exit (CI-01, CI-02)

*(Existing test infrastructure: `pytest.ini` present, `pytest` in `requirements.txt` — no framework install needed)*

---

## Sources

### Primary (HIGH confidence)

- Official GitHub Actions docs — `permissions: contents: write` syntax and GITHUB_TOKEN scopes: https://docs.github.com/en/actions/using-jobs/assigning-permissions-to-jobs
- Python stdlib `datetime` docs — `timezone(timedelta(hours=8))` for fixed UTC offset: https://docs.python.org/3/library/datetime.html#timezone-objects
- Existing codebase — `scripts/mark_done.py` `git_commit_and_push()` function (lines 57–64): confirmed pattern
- Existing codebase — `.github/workflows/morning.yml`: confirmed `actions/checkout@v4`, `actions/setup-python@v5`, Python 3.12 versions
- Existing codebase — `pytest.ini` + `requirements.txt`: confirmed test framework and pythonpath setup

### Secondary (MEDIUM confidence)

- GitHub blog (2023) — Default GITHUB_TOKEN permissions changed to read-only for new repos: https://github.blog/changelog/2023-02-02-github-actions-updating-the-default-github_token-permissions-to-read-only/
- `actions/checkout@v4` README — confirms `origin` remote set correctly for push: https://github.com/actions/checkout

### Tertiary (LOW confidence)

- None — all critical claims verified against official sources or existing codebase.

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — verified against existing `requirements.txt`, workflow files, and Python stdlib docs
- Architecture: HIGH — all patterns derived from existing codebase (`mark_done.py`, `morning.yml`)
- Pitfalls: HIGH — `permissions: contents: write` gap verified against GitHub docs; timezone pitfall verified against Python datetime stdlib

**Research date:** 2026-03-22
**Valid until:** 2026-09-22 (stable domain — GitHub Actions workflow syntax and Python stdlib datetime are highly stable)
