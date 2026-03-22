# Testing Patterns

**Analysis Date:** 2026-03-22

## Test Framework

**Runner:**
- pytest 8.3.5
- Config: `pytest.ini` with `pythonpath = .` to make `scripts/` importable

**Assertion Library:**
- pytest built-in assertions with `assert` statements
- Custom error checking via `pytest.raises(SystemExit)`

**Run Commands:**
```bash
pytest                          # Run all tests
pytest -v                       # Verbose output with test names
pytest tests/test_plan_state.py # Run specific test file
pytest -k test_compute          # Run tests matching pattern
```

## Test File Organization

**Location:**
- Tests are co-located in dedicated `tests/` directory
- One test file per source module: `tests/test_plan_state.py` for `scripts/plan_state.py`, etc.
- Import path: `from scripts.plan_state import ...`

**Naming:**
- Test files: `test_<module>.py`
- Test functions: `test_<function>_<scenario>()` or `test_<scenario>()`
- Examples: `test_compute_plan_day_day1()`, `test_mark_single_block_adds_to_completed()`, `test_evening_0_percent_completion()`

**Structure:**
```
tests/
├── test_plan_state.py      # Tests for scripts/plan_state.py
├── test_generate_task.py    # Tests for scripts/generate_task.py
├── test_mark_done.py        # Tests for scripts/mark_done.py
├── test_check_evening.py    # Tests for scripts/check_evening.py
├── test_push_bark.py        # Tests for scripts/push_bark.py
└── __init__.py              # Empty
```

## Test Structure

**Suite Organization:**

Tests are organized by function, with descriptive names for each scenario:

```python
# --- Temporal computations ---
def test_compute_plan_day_day1():
    start = date(2026, 3, 21)
    assert compute_plan_day(start, start) == 1

def test_compute_plan_day_day8():
    start = date(2026, 3, 21)
    today = start + timedelta(days=7)
    assert compute_plan_day(start, today) == 8

# --- Scene roadmap ---
def test_scene_roadmap_has_7_scenes():
    fixed_scenes = [s for s in SCENE_ROADMAP if s["weeks"][1] <= 14]
    assert len(fixed_scenes) == 7

# --- State I/O ---
def test_load_state_reads_json(tmp_path):
    state_file = tmp_path / "state.json"
    state_file.write_text(json.dumps({...}))
    state = load_state(str(state_file))
    assert state["start_date"] == "2026-03-21"
```

**Patterns:**
- Each test is completely independent with its own setup
- Arrange-Act-Assert pattern: setup variables, call function, assert results
- Comments organize tests into logical groups (commented section headers)

**Test Data Fixtures:**
```python
# In test_check_evening.py:
def make_state(completed=None, skipped=False, ratings=None, start=START):
    today_str = date.today().isoformat()
    return {
        "start_date": start.isoformat(),
        "scene_ratings": ratings or {},
        "daily_log": {
            today_str: {
                "completed": completed or [],
                "skipped": skipped,
            }
        }
    }

# In test_generate_task.py:
SAMPLE_STATE = {
    "start_date": "2026-03-21",
    "scene_ratings": {},
    "daily_log": {},
}

# In test_mark_done.py:
def fresh_state():
    return {
        "start_date": date.today().isoformat(),
        "scene_ratings": {},
        "daily_log": {},
    }
```

## Mocking

**Framework:** `unittest.mock` with `patch` and `MagicMock`

**Patterns:**

```python
# Mock external HTTP calls
from unittest.mock import patch, MagicMock

def test_send_to_bark_calls_correct_url():
    with patch("scripts.push_bark.requests.post") as mock_post:
        mock_post.return_value = MagicMock(status_code=200, text="ok")
        send_to_bark(VALID_PAYLOAD, token="testtoken")
        called_url = mock_post.call_args[0][0]
        assert "testtoken" in called_url

# Mock environment variables
def test_main_uses_bark_token_env_var(monkeypatch):
    monkeypatch.setenv("BARK_TOKEN", "mytoken")
    payload_json = json.dumps({"title": "T", "body": "B", "url": None})
    with patch("scripts.push_bark.send_to_bark") as mock_send:
        with patch("sys.stdin", io.StringIO(payload_json)):
            main()
        _, kwargs = mock_send.call_args
        token_used = kwargs.get("token") or mock_send.call_args[0][1]
        assert token_used == "mytoken"

# Mock stdin
with patch("sys.stdin", io.StringIO(payload_json)):
    main("morning")
```

**What to Mock:**
- External API calls: `requests.post()` in `push_bark.py`
- Environment variables: `monkeypatch.setenv()` for `BARK_TOKEN`
- stdin/stdout: `patch("sys.stdin", io.StringIO(...))` for payload consumption

**What NOT to Mock:**
- Internal functions: call real implementations to test integration
- File system with real tmp_path: use pytest's `tmp_path` fixture for isolated file I/O
- Core business logic: test actual date calculations, state mutations, etc.

## Fixtures and Factories

**Test Data:**

Helper functions create fresh test data:

```python
# Factory pattern for test state
def fresh_state():
    return {
        "start_date": date.today().isoformat(),
        "scene_ratings": {},
        "daily_log": {},
    }

def make_state(completed=None, skipped=False, ratings=None, start=START):
    today_str = date.today().isoformat()
    return {
        "start_date": start.isoformat(),
        "scene_ratings": ratings or {},
        "daily_log": {
            today_str: {
                "completed": completed or [],
                "skipped": skipped,
            }
        }
    }
```

**Built-in pytest Fixtures Used:**
- `tmp_path`: Temporary directory for file I/O tests
- `monkeypatch`: Environment variable and stdin/stdout patching
- `capsys`: Capture stdout/stderr (not used, but available)

**Location:**
- Test data constants at module level: `SAMPLE_STATE`, `VALID_PAYLOAD`, `START = date(2026, 3, 21)`
- Factory functions before test functions: `def make_state(...)`, `def fresh_state()`
- No separate fixtures file; fixtures defined inline in test modules

## Coverage

**Requirements:**
- Not explicitly enforced via configuration (no pytest.ini coverage settings)
- High implicit coverage observed: most code paths tested

**Coverage by Module:**

| Module | Tests | Coverage Areas |
|--------|-------|-----------------|
| `plan_state.py` | 23 | Temporal computations, scene roadmap, state I/O |
| `generate_task.py` | 8 | Payload structure, title format, body content, pre-start edge case |
| `mark_done.py` | 13 | Block marking, deduplication, ratings, immutability |
| `check_evening.py` | 14 | Completion percentage, progress bars, boundaries, biweekly logic |
| `push_bark.py` | 8 | API calls, URL construction, token validation, stdin parsing |

**View Coverage:**
```bash
# No coverage tool configured; run tests with verbose output:
pytest -v
```

## Test Types

**Unit Tests (Primary):**
- Scope: Individual functions in isolation
- Approach: Test temporal calculations, state mutations, payload building
- Examples: `test_compute_plan_day_day1()`, `test_mark_single_block_adds_to_completed()`
- Run with mocks to avoid external dependencies (API calls, file system)

**Integration Tests:**
- Scope: Multiple functions working together with real state
- Approach: Load real `state.json` structure, apply operations, verify results
- Examples: `test_rating_valid_writes_scene_key()` (uses `apply_command()` with `get_scene_for_week()`)
- File I/O tested with actual temp files: `test_load_state_reads_json(tmp_path)`, `test_save_state_writes_json(tmp_path)`

**E2E Tests:**
- Status: Not implemented
- Potential: Could test full workflow (morning payload → Bark API → evening summary) but would require test Bark token

## Common Patterns

**Boundary Testing:**

Edge cases are explicitly tested:

```python
# Plan day boundaries
def test_compute_plan_day_day1():
    assert compute_plan_day(start, start) == 1

def test_compute_plan_day_day8():
    assert compute_plan_day(start, start + timedelta(days=7)) == 8

# Week boundaries
def test_compute_day_within_week_resets():
    assert compute_day_within_week(1) == 1
    assert compute_day_within_week(7) == 7
    assert compute_day_within_week(8) == 1  # Reset after week ends
    assert compute_day_within_week(14) == 7

# Completion percentage boundaries
def test_evening_0_percent_completion():
    payload = build_evening_payload(make_state(completed=[]), today=START)
    assert "0%" in payload["body"]

def test_evening_100_percent_completion():
    payload = build_evening_payload(
        make_state(completed=["review", "input", "extraction", "output"]),
        today=START,
    )
    assert "100%" in payload["body"]
```

**Async Testing:**
- Not applicable (no async code in codebase)

**Error Testing:**

```python
# Test error exit codes
def test_send_to_bark_exits_nonzero_on_api_error():
    with patch("scripts.push_bark.requests.post") as mock_post:
        mock_post.return_value = MagicMock(status_code=400, text="bad request")
        with pytest.raises(SystemExit) as exc:
            send_to_bark(VALID_PAYLOAD, token="testtoken")
        assert exc.value.code != 0

# Test validation errors
def test_rating_invalid_low_raises():
    state = fresh_state()
    with pytest.raises(SystemExit):
        apply_command(state, "rating", rating=0, today=date.today())

# Test invalid input
def test_invalid_block_name_raises():
    state = fresh_state()
    with pytest.raises(SystemExit):
        apply_command(state, "unknown_block", rating=None, today=date.today())
```

**Immutability Testing:**

Critical pattern testing state isolation:

```python
def test_apply_command_does_not_mutate_input():
    state = fresh_state()
    original_log = dict(state["daily_log"])
    apply_command(state, "review", rating=None, today=date.today())
    assert state["daily_log"] == original_log  # Input unchanged
```

## Test Isolation

**State Reset:**
- Each test creates fresh state via `fresh_state()` or `make_state()`
- No shared state between tests
- Date mocking via function parameters: `today=date(2026, 3, 21)`

**File System Isolation:**
- pytest's `tmp_path` fixture creates isolated temp directories
- No test writes to actual `plan/state.json`
- Each test gets fresh file system scope

**Mocking Isolation:**
- All external calls mocked (API, environment variables)
- Mock patches scoped to individual test functions
- No global mock state leakage

---

*Testing analysis: 2026-03-22*
