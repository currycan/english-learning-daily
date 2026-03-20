---
name: progress
description: Show current learning progress — current week/day/scene, today's completion status, overall stats, and scene ratings. Use when the user wants to check where they are in the plan.
---

Read `plan/state.json` and compute the current learning status.

Show:

1. **Current position** — Week N, Day D, Scene name (derived from start_date and today's date using the same formula as `plan_state.py`: `plan_day = (today - start_date).days + 1`, `week = ceil(plan_day / 7)`)
2. **Today's completion** — which blocks are done (✅) and which are pending (⬜): Review / Input / Extraction / Output
3. **Overall stats** — total days elapsed, total days with at least one block completed, overall completion rate
4. **Scene ratings** — list all rated scenes with their scores; note which scenes are unrated
5. **Days remaining** — days left in the 16-week plan

If start_date is in the future, show how many days until the plan begins.

Read the file directly — do not run any scripts.
