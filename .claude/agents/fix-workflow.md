---
name: fix-workflow
description: Diagnose and fix GitHub Actions workflow failures for the morning or evening push jobs. Use when a workflow run fails or notifications stop arriving.
---

Diagnose GitHub Actions failures for this project.

## Common failure causes

1. **ModuleNotFoundError: No module named 'scripts'** — workflow must use `python -m scripts.generate_task` not `python scripts/generate_task.py`. Check `.github/workflows/morning.yml` and `evening.yml`.

2. **Bark API 400 "failed to get device token"** — `BARK_TOKEN` secret is wrong or expired. User must open Bark app on iPhone, copy the token, and update the secret at: GitHub repo → Settings → Secrets and variables → Actions → BARK_TOKEN.

3. **Bark API 4xx/5xx other** — show the full error response body. Could be rate limit or Bark service issue.

4. **state.json missing or malformed** — check that `plan/state.json` exists and is valid JSON with `start_date`, `scene_ratings`, and `daily_log` fields.

5. **pip install fails** — check `requirements.txt` for syntax errors.

## Steps

1. Ask the user to paste the failed workflow run log, or offer to check the workflow files directly
2. Identify which step failed and what the error message says
3. Apply the fix
4. Tell the user how to re-run: GitHub repo → Actions → select workflow → Re-run failed jobs
