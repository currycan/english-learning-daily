# Technology Stack

**Analysis Date:** 2026-03-22

## Languages

**Primary:**
- Python 3.12+ - All application logic, CLI utilities, and task generation

## Runtime

**Environment:**
- Python 3.12+ (Ubuntu-latest in CI/CD, local development uses Python 3.14.3)

**Package Manager:**
- pip
- Lockfile: `requirements.txt` (project-level dependencies only)

## Frameworks

**Testing:**
- pytest 8.3.5 - Unit and integration test framework
- pytest-cov 7.0.0 - Code coverage reporting

**Build/Dev:**
- GitHub Actions - CI/CD orchestration

## Key Dependencies

**Critical:**
- requests 2.32.3 - HTTP client for Bark API integration (push notifications)
- pytest 8.3.5 - Test execution framework
- pytest-cov 7.0.0 - Code coverage measurement

**Infrastructure:**
- None - No web framework, database ORM, or external infrastructure libraries

## Configuration

**Environment:**
- GitHub Secrets: `BARK_TOKEN` (required for push notifications)
- Config file: `plan/config.json` - Non-sensitive configuration (push times, timezone)
- State file: `plan/state.json` - User progress and scene ratings (JSON)

**Build:**
- GitHub Actions workflow files: `.github/workflows/morning.yml` and `.github/workflows/evening.yml`
- No build system (pure Python scripts, no compilation)

## Platform Requirements

**Development:**
- Python 3.12+
- Git (for `mark_done.py` commit/push operations)

**Production:**
- Python 3.12+ (workflow runs on Ubuntu-latest)
- Git credentials for auto-commits
- BARK_TOKEN environment variable (from GitHub Secrets)

## Design Pattern

**Data Flow Architecture:**
- stdout → stdin JSON pipe pattern
- Scripts communicate via JSON serialization
- No server framework; entirely script-based

**State Management:**
- Single source of truth: `plan/state.json`
- Immutable state updates using `copy.deepcopy()`
- Temporal calculations derived from `start_date` at runtime

---

*Stack analysis: 2026-03-22*
