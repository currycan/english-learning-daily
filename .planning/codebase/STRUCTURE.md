# Codebase Structure

**Analysis Date:** 2026-03-22

## Directory Layout

```
study-all/
├── .github/workflows/      # GitHub Actions automation (CI/CD entry points)
│   ├── morning.yml         # Trigger morning task push (daily 23:00 UTC)
│   └── evening.yml         # Trigger evening summary push (daily 13:00 UTC)
├── .planning/              # Planning and analysis documents
│   └── codebase/           # Architecture and structure documentation
├── plan/                   # State and configuration data
│   ├── state.json          # Source of truth: start date, scene ratings, daily log
│   └── config.json         # Push times and timezone (non-secret configuration)
├── scripts/                # Core application logic (all executable modules)
│   ├── __init__.py         # Package marker
│   ├── plan_state.py       # Temporal calculation + state I/O (depended on by all)
│   ├── generate_task.py    # Morning payload builder (entry point 1)
│   ├── check_evening.py    # Evening payload builder (entry point 2)
│   ├── push_bark.py        # Bark API client (entry point 3)
│   └── mark_done.py        # CLI state mutation tool (entry point 4)
├── tests/                  # Test suite (co-located with codebase)
│   ├── __init__.py         # Package marker
│   ├── test_plan_state.py  # Tests for temporal + state functions
│   ├── test_generate_task.py   # Tests for morning payload builder
│   ├── test_check_evening.py   # Tests for evening payload builder
│   ├── test_push_bark.py   # Tests for Bark API client
│   └── test_mark_done.py   # Tests for state mutation logic
├── docs/                   # Documentation (not code)
├── .pytest_cache/          # Pytest cache (generated, not committed)
├── .coverage               # Coverage report (generated, not committed)
├── pytest.ini              # Pytest configuration
├── requirements.txt        # Python dependencies
├── README.md               # User-facing documentation (Chinese + English)
├── CLAUDE.md               # Project configuration and constraints
└── .gitignore              # Git ignore rules

```

## Directory Purposes

**`.github/workflows/`:**
- Purpose: GitHub Actions automation that triggers scripts on schedule
- Contains: YAML workflow definitions
- Key files: `morning.yml` (07:00 BJT), `evening.yml` (21:00 BJT)

**`plan/`:**
- Purpose: Application state and configuration (not code)
- Contains: JSON files with learning progress and settings
- Key files:
  - `state.json`: Daily completion log, scene ratings, start date (mutable, user-edited)
  - `config.json`: Push times, timezone (static configuration)

**`scripts/`:**
- Purpose: Core application logic; all directly runnable modules
- Contains: Python scripts implementing state management, content generation, delivery
- Naming: Each file is an executable entry point or shared utility
- Dependencies: `plan_state.py` is depended on by all others

**`tests/`:**
- Purpose: Test suite using pytest framework
- Naming: Mirrors source files with `test_` prefix pattern
- Co-location: Tests live in same repo (not in separate directory)
- Run: `pytest` (all), `pytest tests/test_plan_state.py` (single file)

**`.planning/codebase/`:**
- Purpose: Architecture and codebase analysis documents (GSD mapping)
- Contains: ARCHITECTURE.md, STRUCTURE.md, CONVENTIONS.md, TESTING.md (when applicable)

## Key File Locations

**Entry Points:**

| File | Purpose | Trigger |
|------|---------|---------|
| `scripts/generate_task.py` | Generate morning notification payload | GitHub Actions 23:00 UTC or manual run |
| `scripts/check_evening.py` | Generate evening summary payload | GitHub Actions 13:00 UTC or manual run |
| `scripts/push_bark.py` | Deliver JSON payload to Bark API | Pipe input from above |
| `scripts/mark_done.py` | Record user progress, update state, commit | Manual CLI invocation |

**State and Configuration:**

| File | Responsibility |
|------|-----------------|
| `plan/state.json` | Source of truth: start_date, scene_ratings, daily_log (user-mutable) |
| `plan/config.json` | Push times and timezone (static after setup) |

**Core Logic:**

| File | Responsibility |
|------|-----------------|
| `scripts/plan_state.py` | Temporal calculations, state I/O, scene lookup (depended on by all) |
| `scripts/generate_task.py` | Build morning push content from state |
| `scripts/check_evening.py` | Build evening summary from daily_log |
| `scripts/push_bark.py` | HTTP client for Bark API |
| `scripts/mark_done.py` | Immutable state updates + git integration |

**Testing:**

| File | Scope |
|------|-------|
| `tests/test_plan_state.py` | Temporal math, state I/O, scene selection |
| `tests/test_generate_task.py` | Morning payload builder |
| `tests/test_check_evening.py` | Evening payload builder, completion tracking |
| `tests/test_push_bark.py` | Bark API client, error handling |
| `tests/test_mark_done.py` | State mutation, CLI argument parsing |

## Naming Conventions

**Files:**
- Executable scripts: `snake_case.py` (e.g., `generate_task.py`)
- Test files: `test_<module>.py` (e.g., `test_plan_state.py`)
- State files: `<descriptor>.json` (e.g., `state.json`, `config.json`)

**Directories:**
- Functional domains: `<function>` (scripts, tests, .github)
- Support: `.<name>` (hidden, e.g., `.planning`, `.pytest_cache`)
- Data: `<name>` (e.g., `plan`, `docs`)

**Python Modules:**
- Functions: `snake_case` (e.g., `compute_plan_day()`, `build_morning_payload()`)
- Classes: None used (functional style)
- Constants: `UPPER_SNAKE_CASE` (e.g., `SCENE_ROADMAP`, `VALID_BLOCKS`)
- Files as packages: Include `__init__.py` to enable `-m` imports

**JSON Schemas:**
- state.json: `{"start_date": "YYYY-MM-DD", "scene_ratings": {str: 1-5}, "daily_log": {ISO_date: {"completed": [str], "skipped": bool}}}`
- config.json: `{"morning_hour": int, "evening_hour": int, "weekly_recording_day": str, "timezone": str}`
- Payload: `{"title": str, "body": str, "url": str | null}`

## Where to Add New Code

**New Feature (e.g., new payload type):**
- Primary code: Create `scripts/new_feature.py` with builder function (e.g., `build_weekly_summary()`)
- Tests: Create `tests/test_new_feature.py` with test functions
- Integration: Add to GitHub workflow YAML if it's a scheduled push
- Pattern: Import functions from `scripts/plan_state.py` for temporal calculations; return JSON envelope

**New Temporal Calculation:**
- Implementation: Add function to `scripts/plan_state.py` (e.g., `compute_X()`)
- Tests: Add to `tests/test_plan_state.py`
- Pattern: Pure function taking `start_date` and `today`, returning computed integer/bool
- Usage: Import in `scripts/generate_task.py` or `scripts/check_evening.py`

**New State Mutation Command:**
- Implementation: Add to `VALID_BLOCKS` set in `scripts/mark_done.py`
- Logic: Add branch in `apply_command()` function to handle new command
- Tests: Add to `tests/test_mark_done.py` with test case for new command
- Pattern: Command modifies `state["daily_log"][today_str]` or `state["scene_ratings"]`; immutably

**New Configuration:**
- Add to `plan/config.json` with default values
- Load: Add lookup in relevant script (e.g., `generate_task.py` if time-dependent)
- Tests: Add to `tests/` if configuration logic needs testing

**Utilities:**
- Shared helpers: Add to `scripts/plan_state.py` if temporal/state-related
- Otherwise: Create new module in `scripts/` and import in calling scripts
- Test: Co-locate test with caller module

## Special Directories

**`venv/`:**
- Purpose: Python virtual environment with dependencies
- Generated: Yes (via `pip install -r requirements.txt`)
- Committed: No (in .gitignore)

**`.pytest_cache/`:**
- Purpose: Pytest caching for faster test runs
- Generated: Yes (by pytest automatically)
- Committed: No

**`.coverage`:**
- Purpose: Coverage report data
- Generated: Yes (by coverage.py tool)
- Committed: No

**`.github/`:**
- Purpose: GitHub-specific configuration (workflows, issue templates)
- Committed: Yes
- CI/CD entry point: Workflows trigger `python -m scripts.module_name` commands

**`.planning/codebase/`:**
- Purpose: Generated analysis and mapping documents (GSD)
- Generated: Yes (by gsd:map-codebase agent)
- Committed: Yes (reference for future code changes)

## Module Import Pattern

All scripts use `-m` module invocation from project root:

```bash
# Do this (so scripts/ package is importable)
python -m scripts.generate_task
python -m scripts.mark_done review

# Not this (would fail because scripts/ not in PYTHONPATH)
python scripts/generate_task.py
```

Rationale: Enables `from scripts.plan_state import ...` in other modules.

---

*Structure analysis: 2026-03-22*
