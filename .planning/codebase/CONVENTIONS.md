# Coding Conventions

**Analysis Date:** 2026-03-22

## Naming Patterns

**Files:**
- Lowercase with underscores: `plan_state.py`, `generate_task.py`, `mark_done.py`, `check_evening.py`, `push_bark.py`
- Test files prefixed with `test_`: `test_plan_state.py`, `test_generate_task.py`, etc.
- Scripts are executable modules in `scripts/` directory; tests in `tests/` directory

**Functions:**
- Snake_case for all function names: `compute_plan_day()`, `load_state()`, `send_to_bark()`, `build_morning_payload()`
- Helper functions use underscores: `compute_current_week()`, `is_biweekly_checkin()`, `git_commit_and_push()`
- Main entry point always named `main()`: `scripts/mark_done.py`, `scripts/push_bark.py`

**Variables:**
- Snake_case throughout: `start_date`, `scene_ratings`, `daily_log`, `plan_day`, `push_type`, `post_data`
- Constants in UPPER_CASE: `SCENE_ROADMAP`, `VALID_BLOCKS`, `STATE_PATH`, `BARK_BASE_URL`
- Module-level constants: `BLOCKS` (list), `BARK_BASE_URL` (string)

**Types:**
- Use built-in types with no type aliases: `dict`, `int`, `str`, `bool`, `date`
- Type hints in function signatures: `def compute_plan_day(start_date: date, today: date) -> int:`
- Dict/list types specified with generics when complex: `dict[str, dict[str, list[str]]]` for daily_log

## Code Style

**Formatting:**
- No explicit formatter configured (no `.black`, `.ruff`, or `.flake8` files present)
- Standard Python conventions followed: 2-space indentation for nested structures, 4-space indentation for function bodies
- Line length appears unconstrained but pragmatic (max observed ~100 chars in structured data)
- Consistent spacing around operators: `week <= 14`, `plan_day - 1`

**Linting:**
- No linter configured or enforced
- Code follows PEP 8 conventions implicitly (camelCase avoided, underscores standard)

## Import Organization

**Order:**
1. Standard library imports: `import json`, `import sys`, `import math`, `import os`, `import subprocess`, `from datetime import date`, `from pathlib import Path`, `import copy`
2. Third-party imports: `import requests`, `import pytest`
3. Local imports: `from scripts.plan_state import ...`

**Path Aliases:**
- No path aliases used
- Relative imports from same package: `from scripts.plan_state import` (used across all modules)
- Imports grouped by their module: `from scripts.plan_state import compute_plan_day, compute_current_week, ...`

**Example from `mark_done.py`:**
```python
import copy
import json
import os
import subprocess
import sys
from datetime import date
from pathlib import Path

from scripts.plan_state import (
    compute_plan_day,
    compute_current_week,
    get_scene_for_week,
    load_state,
    save_state,
)
```

## Error Handling

**Patterns:**
- Explicit error handling at system boundaries: `try/except` around file I/O and JSON parsing
- `sys.exit(1)` on all errors to signal failure to orchestrators (GitHub Actions)
- Error messages printed to `stderr` using `file=sys.stderr`
- Error context included in messages: `f"ERROR: Cannot load state from {path}: {e}"`

**Examples:**
```python
# File I/O errors
try:
    return json.loads(Path(path).read_text())
except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f"ERROR: Cannot load state from {path}: {e}", file=sys.stderr)
    sys.exit(1)

# API errors
if response.status_code < 200 or response.status_code >= 300:
    print(f"ERROR: Bark API returned {response.status_code}: {response.text}", file=sys.stderr)
    sys.exit(1)

# Validation errors
if command not in VALID_BLOCKS and command != "rating":
    print(f"ERROR: Unknown command '{command}'. Valid: {sorted(VALID_BLOCKS)} or 'rating <1-5>'", file=sys.stderr)
    sys.exit(1)
```

## Logging

**Framework:** Console output using `print()`

**Patterns:**
- Status messages to stdout: `print(f"[{push_type}] Sending Bark notification: {payload['title']}")`
- Success confirmations to stdout: `print(f"✓ Marked '{command}' — state updated and pushed.")`
- Error messages to stderr: `print(f"ERROR: ...", file=sys.stderr)`
- Structured payload logging: JSON payloads printed for debugging via `print(json.dumps(payload, ensure_ascii=False))`

**When to Log:**
- Status updates on script execution: beginning and completion
- Errors with context: file paths, API responses, user input
- Success confirmations after mutations

## Comments

**When to Comment:**
- Complex temporal logic explained inline: `# Weeks 15-16: resolve by lowest rating`
- State schema documented at module level: comments near SCENE_ROADMAP definition
- Biweekly boundary calculations explained: `# scene_cycle_day 14 always lands on day_within_week 7 (7th day of 2nd week)`
- Fallback logic for backwards compatibility: `# If not found, try to find the entry using date.today() (for backwards compatibility)`

**JSDoc/TSDoc:**
- Not used; Python docstrings not present in codebase
- Function signatures include type hints sufficient for understanding

## Function Design

**Size:**
- Typical functions 10-30 lines
- Largest functions `build_morning_payload()` (30 lines) and `build_evening_payload()` (50+ lines with explanatory text)
- Short utility functions 1-5 lines: `compute_plan_day()`, `is_biweekly_checkin()`

**Parameters:**
- 1-4 parameters per function
- Type hints required for clarity: `def apply_command(state: dict, command: str, rating, today: date) -> dict:`
- Default parameters for optional dates: `def build_morning_payload(state: dict, today: date = None) -> dict:`

**Return Values:**
- Explicit return types specified in signature
- Dictionaries for structured data: `{"title": str, "body": str, "url": str | None}`
- None returned when appropriate: `save_state()` returns None
- Computed values returned, never printed directly

## Module Design

**Exports:**
- Explicit imports listed at module top for clarity
- `main()` entry point convention for executable modules
- Shared utilities (`plan_state.py`) exported as functions imported by others
- Constants defined at module level and imported: `VALID_BLOCKS`, `SCENE_ROADMAP`, `BARK_BASE_URL`

**Barrel Files:**
- Not used; each module imports directly from source
- `scripts/__init__.py` and `tests/__init__.py` are empty

**Immutability Pattern (CRITICAL):**
- Input state objects never mutated in-place
- `apply_command()` uses `copy.deepcopy(state)` at entry: `state = copy.deepcopy(state)`
- Returns new modified copy: `return state` (modified copy)
- Original passed to function remains unchanged
- Example:
```python
def apply_command(state: dict, command: str, rating, today: date) -> dict:
    state = copy.deepcopy(state)  # CRITICAL: Copy at start
    # ... modifications to state ...
    return state
```

---

*Convention analysis: 2026-03-22*
