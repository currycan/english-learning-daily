# Architecture

**Analysis Date:** 2026-03-22

## Pattern Overview

**Overall:** Unix pipeline architecture with modular temporal computation

**Key Characteristics:**
- State-driven with single source of truth (`plan/state.json`)
- Derived computation: all temporal values calculated from `start_date` at runtime, never stored
- Process composition via stdout→stdin JSON pipes
- Immutable state mutations using deep copy
- Decoupled concern separation: temporal logic, payload generation, push delivery

## Layers

**Temporal Computation Layer:**
- Purpose: Calculate all time-derived values (current week, plan day, scene cycle day)
- Location: `scripts/plan_state.py`
- Contains: `compute_plan_day()`, `compute_current_week()`, `compute_day_within_week()`, `compute_scene_cycle_day()`, `is_biweekly_checkin()`, `get_scene_for_week()`
- Depends on: Python datetime library, SCENE_ROADMAP constant
- Used by: All task generation and state mutation scripts

**State Persistence Layer:**
- Purpose: Load and save state atomically
- Location: `scripts/plan_state.py` (`load_state()`, `save_state()`)
- Contains: JSON I/O with error handling
- Depends on: pathlib, json
- Used by: All scripts that read or write `plan/state.json`

**Content Generation Layer:**
- Purpose: Transform state and temporal data into notification payloads
- Location: `scripts/generate_task.py`, `scripts/check_evening.py`
- Contains: `build_morning_payload()`, `build_evening_payload()`
- Depends on: Temporal computation layer, state persistence layer
- Used by: Push delivery layer via stdout

**Push Delivery Layer:**
- Purpose: Send JSON payloads to external Bark API
- Location: `scripts/push_bark.py`
- Contains: `send_to_bark()`, stdin JSON reader, error handling
- Depends on: requests library, BARK_TOKEN from environment
- Used by: GitHub Actions workflows

**State Mutation Layer:**
- Purpose: Record user progress and apply immutable state updates
- Location: `scripts/mark_done.py`
- Contains: `apply_command()`, git integration
- Depends on: Temporal computation, state persistence, subprocess (git)
- Used by: Local CLI invocations and manual state updates

## Data Flow

**Morning Push Workflow:**
1. GitHub Actions triggers at 23:00 UTC (07:00 BJT)
2. `generate_task.py` runs: loads `plan/state.json` → computes temporal values → calls `build_morning_payload()` → outputs JSON to stdout
3. Pipe to `push_bark.py` via `|` (stdin)
4. `push_bark.py` reads JSON from stdin → reads `BARK_TOKEN` from environment → POST to Bark API
5. Notification delivered to iPhone

**Evening Push Workflow:**
1. GitHub Actions triggers at 13:00 UTC (21:00 BJT)
2. `check_evening.py` runs: loads `plan/state.json` → reads daily_log for today → computes completion % → calls `build_evening_payload()` → outputs JSON to stdout
3. Same pipe-to-Bark pattern as morning
4. Biweekly check-in reminder added when `is_biweekly_checkin()` returns true (day 14 of 2-week cycle)

**State Update Workflow:**
1. User runs `python -m scripts.mark_done <command> [value]`
2. Script loads state → deep copies state → applies command to copy (immutable) → saves updated copy → git commit → git push
3. Next scheduled push reads updated state

**State Management:**
- Single source of truth: `plan/state.json` containing only:
  - `start_date`: ISO date string (used to derive all time values)
  - `scene_ratings`: dict mapping scene name → 1-5 rating
  - `daily_log`: dict mapping ISO date string → completion record
- All computed fields (week, day, scene, plan_day) derived fresh at runtime from `start_date`
- No caching of temporal data in state file

## Key Abstractions

**SCENE_ROADMAP:**
- Purpose: Maps weeks 1-14 to 7 scenes (2 weeks each), defines scene metadata
- Examples: `scripts/plan_state.py` lines 7-106
- Pattern: List of dicts with weeks tuple, scene name, podcast source, article source, AI prompt
- Used by: Scene lookup via `get_scene_for_week()` and content generation

**Temporal Functions:**
- Purpose: Isolate date math from business logic
- Examples: `compute_plan_day()` (days since start), `compute_current_week()` (week ceiling), `compute_scene_cycle_day()` (position in 2-week cycle)
- Pattern: Pure functions taking start_date and today, returning computed integers
- Benefit: Easy to test; all time logic centralized

**JSON Envelope Pattern:**
- Purpose: Uniform payload format for Bark API
- Pattern: `{"title": str, "body": str, "url": str | null}`
- Used by: Both morning and evening payloads
- Benefit: Decouples content generation from delivery

**Immutable State Pattern:**
- Purpose: Prevent accidental mutations in `apply_command()`
- Pattern: `state = copy.deepcopy(state)` at function entry, modify copy, return copy
- Location: `scripts/mark_done.py` line 22
- Benefit: Pure function semantics; caller's state never changed

## Entry Points

**Morning Task Generation (`scripts/generate_task.py`):**
- Location: `scripts/generate_task.py` lines 56-59
- Triggers: GitHub Actions schedule 23:00 UTC daily
- Responsibilities: Load state, compute plan_day + week + scene, format task content (Review/Input/Extraction/Output), output JSON
- Pre-start: Returns "Plan starts in X days" message

**Evening Summary (`scripts/check_evening.py`):**
- Location: `scripts/check_evening.py` lines 100-103
- Triggers: GitHub Actions schedule 13:00 UTC daily
- Responsibilities: Load state, find today's completion record, compute completion %, detect biweekly check-in, output JSON
- Fallback: Uses first available daily_log entry if exact date not found

**Bark Delivery (`scripts/push_bark.py`):**
- Location: `scripts/push_bark.py` lines 31-42
- Triggers: Receives JSON via stdin from pipe
- Responsibilities: Read JSON, validate BARK_TOKEN environment variable, POST to Bark API, handle errors with non-zero exit
- Error handling: Exit code 1 on missing token or API error

**State Update CLI (`scripts/mark_done.py`):**
- Location: `scripts/mark_done.py` lines 67-94
- Triggers: Manual invocation `python -m scripts.mark_done <command> [value]`
- Responsibilities: Parse CLI args, apply immutable state mutation, save state, git commit, git push
- Valid commands: review, input, extraction, output, all, skip, rating <1-5>

## Error Handling

**Strategy:** Defensive with explicit error messages and non-zero exit codes for orchestration

**Patterns:**
- JSON decode errors: `json.JSONDecodeError` → `sys.exit(1)` with context message
- Missing state file: `FileNotFoundError` → caught and logged to stderr with path
- API failures: HTTP status outside 200-299 range → log response text and exit
- Missing environment variables: `BARK_TOKEN` absence → error message to stderr, non-zero exit
- Invalid input: `ValueError` on integer rating → caught and logged with got value
- Git operations: `subprocess.CalledProcessError` → caught and logged

All errors printed to `sys.stderr`; all exit codes are 0 (success) or 1 (failure).

## Cross-Cutting Concerns

**Logging:**
- Approach: Explicit print statements to stdout for user messages, stderr for errors
- Pattern: `print(message, file=sys.stderr)` for errors, bare `print()` for info
- Example: `scripts/push_bark.py` line 40 logs push type and title

**Validation:**
- Dates: Parsed via `date.fromisoformat()` or `date.today()` (delegated to datetime module)
- Integers: `isinstance(rating, int)` checks; bounds checked 1-5
- JSON: `json.loads()` with exception handling; expected keys accessed with `.get()` defaults
- Commands: Against whitelist in `VALID_BLOCKS` set

**Authentication:**
- Approach: Environment variable only (`BARK_TOKEN`)
- Constraint: Never hardcoded; must be set at runtime by GitHub Actions or user shell
- Validation: Checked for non-empty string before API call

**Immutability:**
- Pattern: Critical in `apply_command()` where input state is deep-copied before mutation
- Enforced via `copy.deepcopy(state)` at function entry
- Benefit: Caller's state remains unchanged; function is pure

**Temporal Consistency:**
- All time values derived from single `start_date` field
- Computed fresh on each run (no caching)
- Supports "pre-start" state (plan_day ≤ 0) with graceful messaging
- Scene selection: weeks 1-14 use SCENE_ROADMAP; weeks 15-16 auto-select lowest-rated scene

---

*Architecture analysis: 2026-03-22*
