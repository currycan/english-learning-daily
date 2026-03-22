# Domain Pitfalls

**Domain:** Automated RSS-to-AI-content pipeline with GitHub Actions and git commit output
**Researched:** 2026-03-22
**Confidence:** MEDIUM (reasoning from deep domain knowledge; web search unavailable)

---

## Critical Pitfalls

Mistakes that cause silent failures, data loss, or pipeline breakdown.

---

### Pitfall 1: GitHub Actions Scheduled Workflows Are Not Guaranteed to Run

**What goes wrong:** GitHub silently skips or delays scheduled cron jobs on free-tier repos, especially if the repo has had no activity for 60 days. Runs may be delayed by 15–60 minutes or skipped entirely under high platform load. The cron fires at UTC, but runner availability is not guaranteed.

**Why it happens:** GitHub's scheduler is best-effort for free accounts. Inactive repositories get deprioritized. This project's existing `morning.yml` runs at `0 23 * * *` — any scheduler instability means the daily content commit is silently skipped with no alert.

**Consequences:** Days are silently missing from `content/`. The user has no awareness of gaps unless they check the git log manually.

**Prevention:**
- Always keep `workflow_dispatch` enabled (already done) for manual recovery.
- Add a step that sends a Bark failure notification if the content script fails, so silent skips surface as alerts.
- Consider a weekly "check for gaps" cron that scans `content/` for missing dates and alerts.
- Commit any small activity to keep the repo active if using a free account.

**Detection:** Check Actions > workflow run history for gaps. Add an explicit `if: failure()` notification step to the workflow.

**Phase:** Content pipeline workflow (Phase 1 or 2).

---

### Pitfall 2: RSS Feed Structure Changes Without Warning

**What goes wrong:** VOA Learning English and BBC Learning English RSS feeds change their item format, namespaces, or URL structure with no announcement. Fields that exist today (`<content:encoded>`, `<description>`, `<link>`) may shift format, get removed, or get wrapped in CDATA blocks differently.

**Why it happens:** Feed publishers update their CMS systems. RSS is not a stable API — it is an HTML scraping layer dressed as a standard. VOA in particular has reorganized its feed URLs multiple times.

**Consequences:** The article body extracted is empty, truncated, or raw HTML tags. Claude API is called with garbage input and produces garbage output, or the prompt fails validation. The file is committed with no usable article content.

**Prevention:**
- Parse feeds with `feedparser` library (handles namespace quirks, CDATA, malformed XML) rather than raw `xml.etree.ElementTree` or string parsing.
- After fetching, validate that extracted article text meets a minimum length threshold (e.g., 200 characters) before proceeding to AI generation.
- Log the raw feed item structure on first use so future structural diffs are detectable.
- Treat article body extraction as a separate, isolated function with explicit validation.

**Detection:** Content files that are shorter than 500 characters total are a warning sign. Add an assertion in the fetch script.

**Phase:** RSS fetch module (Phase 1).

---

### Pitfall 3: Committing to Git from CI Without Proper Identity and Permissions

**What goes wrong:** The new content script must commit `content/YYYY-MM-DD.md` back to the repo from within GitHub Actions. This requires: `git config user.email`, `git config user.name`, and using `GITHUB_TOKEN` with write permissions. Missing any of these causes the commit step to fail silently or with a cryptic error.

**Why it happens:** The default `GITHUB_TOKEN` in Actions has `read` permissions by default in newer GitHub policy. The `actions/checkout@v4` action checks out a detached HEAD or shallow clone by default. `git push` fails unless `persist-credentials: true` is set on the checkout step.

**Consequences:** Content is generated and discarded. The workflow appears to succeed if the commit step error is not checked explicitly. Files accumulate in the runner workspace and are lost.

**Prevention:**
- Add `permissions: contents: write` to the workflow job.
- Use `actions/checkout@v4` with `persist-credentials: true` (the default, but verify).
- Always set git identity before committing: `git config user.name "github-actions[bot]"` and `git config user.email "github-actions[bot]@users.noreply.github.com"`.
- Use `git diff --exit-code` before `git commit` to skip commits when file already exists for the day (duplicate-skip requirement).
- Push with `git push origin HEAD:master` explicitly rather than relying on tracking.

**Detection:** Workflow run shows green but no new file appears in repo. Check the commit step output explicitly.

**Phase:** CI workflow for content commit (Phase 1 or 2).

---

### Pitfall 4: Claude API Prompt That Produces Inconsistent Structure

**What goes wrong:** The Claude API prompt asks for vocabulary words and comprehension questions, but the response format varies between calls: sometimes numbered lists, sometimes bullet points, sometimes prose. Downstream parsing to build the Markdown file breaks on unexpected formats.

**Why it happens:** Claude models are probabilistic. Without a strict output format constraint in the prompt (ideally JSON schema), the model uses stylistic variation across runs. Temperature, model version changes, and prompt wording all affect structure.

**Consequences:** The committed Markdown file has inconsistent formatting. Vocabulary sections appear as prose in some files and lists in others. If parsing is attempted (not just raw inclusion), the parser silently produces empty sections.

**Prevention:**
- Include explicit format instructions in the prompt: "Respond ONLY with the following JSON structure: {...}". Then parse JSON and render to Markdown in Python — never trust Claude to produce finished Markdown directly.
- Alternatively, use XML-delimited sections (`<vocabulary>...</vocabulary>`) which are easier to extract reliably.
- Validate the parsed response structure before writing the file. If parsing fails, write a fallback file with raw Claude output rather than an empty file.
- Pin a specific Claude model version (e.g., `claude-3-5-haiku-20241022`) rather than a floating alias so model updates don't change behavior.

**Detection:** Spot-check generated files across multiple days for structural consistency.

**Phase:** Claude API integration (Phase 2).

---

### Pitfall 5: Duplicate Article Commits Due to Clock/Timezone Mismatch

**What goes wrong:** The workflow runs at UTC time. `content/YYYY-MM-DD.md` uses the date as the filename. If the workflow runs at 23:00 UTC (07:00 BJT) but `date.today()` in Python resolves in UTC on the runner, the file is named one day behind relative to the user's local date.

**Why it happens:** GitHub Actions runners always operate in UTC. `datetime.date.today()` returns the UTC date, not BJT (UTC+8). At 23:00 UTC, it is already tomorrow in Beijing. A file named `2026-03-22.md` committed by a 23:00 UTC cron is actually content for 2026-03-23 in the user's timezone.

**Consequences:** Either: (a) the file is named the wrong date and confuses the library, or (b) the existing state system (`plan/state.json`) uses a different date than the content filenames, breaking any future integration.

**Prevention:**
- In the content script, derive the target date using an explicit timezone offset: `date.today() + timedelta(hours=8)` when running under UTC.
- Or pass the target date as an environment variable in the workflow: `TARGET_DATE=$(TZ='Asia/Shanghai' date +%Y-%m-%d)` and read it in the Python script.
- Decide on the convention (UTC date or BJT date) and document it as a constant in the codebase — never derive it implicitly from the system clock.

**Detection:** Compare filename dates in `content/` against the workflow run timestamps in Actions history.

**Phase:** CI workflow and content script date handling (Phase 1).

---

## Moderate Pitfalls

---

### Pitfall 6: RSS Fetching Blocked by User-Agent Filtering

**What goes wrong:** Some RSS endpoints (BBC in particular) return 403 or redirect to a captcha/error page when the `requests` default User-Agent (`python-requests/2.x.x`) is detected as a bot.

**Prevention:** Set a realistic `User-Agent` header on all RSS requests: `"Mozilla/5.0 (compatible; StudyBot/1.0)"`. Add a `timeout=15` to all HTTP calls to avoid hanging the workflow. Handle non-200 status codes explicitly with `sys.exit(1)`.

**Phase:** RSS fetch module (Phase 1).

---

### Pitfall 7: Claude API Cost Overrun From Retry Loops

**What goes wrong:** A retry loop around the Claude API call on transient errors (rate limits, 529 overload) can fire multiple times in one run, multiplying API cost. At one call per day this is negligible, but a misconfigured retry with no backoff can generate 10+ calls in a single workflow run.

**Prevention:** Use exponential backoff with a hard maximum of 3 retries. Log every API call attempt. For this project's scale (one call per day), a simple "try once, fail cleanly" policy is safer than retry logic — let the user trigger manually if it fails.

**Phase:** Claude API integration (Phase 2).

---

### Pitfall 8: Article Already Fetched Today — No Deduplication Guard

**What goes wrong:** The workflow runs once daily, but `workflow_dispatch` allows manual reruns. If the file `content/YYYY-MM-DD.md` already exists, the script overwrites it with a different article (because RSS feeds rotate items), producing inconsistent content for the same date.

**Prevention:** Check for file existence before fetching: if `content/{today}.md` exists, skip all fetch and AI steps and exit 0 cleanly. This is already listed in the project requirements ("skip duplicate commits if article already exists") but needs explicit implementation — it is easy to forget in the happy path.

**Detection:** Manually trigger the workflow twice on the same day and verify the file is not changed.

**Phase:** Content pipeline script (Phase 1 or 2).

---

### Pitfall 9: Anthropic SDK Version Not Pinned

**What goes wrong:** `anthropic` is not currently in `requirements.txt`. When added without pinning, future pip installs pick up breaking SDK changes. The Anthropic Python SDK has had multiple breaking API shape changes between major versions (v0.x → v0.2x → v0.3x), including changes to `client.messages.create()` parameter names and response object shape.

**Prevention:** Pin the exact version: `anthropic==0.49.0` (or whichever is current at implementation time). Add to `requirements.txt` with the exact version, same as `requests==2.32.3` already is.

**Phase:** Project setup / dependency management (Phase 1).

---

## Minor Pitfalls

---

### Pitfall 10: Markdown File Encoding Issues With Non-ASCII Article Content

**What goes wrong:** VOA articles occasionally contain smart quotes, em-dashes, or non-ASCII characters. Writing with default Python file I/O on a Linux runner uses UTF-8, but if `ensure_ascii=True` is used anywhere in the pipeline, non-ASCII characters are escaped as `\uXXXX` in the output file.

**Prevention:** Always open files with `encoding="utf-8"` explicitly. Use `ensure_ascii=False` in any `json.dumps` calls (already done in existing code). Test with an article that contains non-ASCII content.

**Phase:** File writing (Phase 2).

---

### Pitfall 11: Empty `content/` Directory Not Committed to Git

**What goes wrong:** Git does not track empty directories. If the `content/` directory does not exist when the workflow first runs, `open("content/YYYY-MM-DD.md", "w")` raises `FileNotFoundError` and the workflow fails.

**Prevention:** Either pre-create `content/.gitkeep` in the repo, or add `Path("content").mkdir(exist_ok=True)` at the start of the content commit script.

**Phase:** Repo setup (before Phase 1 implementation).

---

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation |
|-------------|---------------|------------|
| RSS fetch script | Feed structure change, User-Agent block | Use `feedparser`, validate minimum text length, set User-Agent header |
| Claude API call | Non-deterministic response structure | Use JSON output mode in prompt; parse and validate before writing |
| CI workflow (git commit) | Missing write permissions, timezone date mismatch | Add `permissions: contents: write`, derive date with explicit timezone |
| Duplicate-skip logic | Overwrite on manual rerun | File existence check before fetch — skip entire pipeline, exit 0 |
| Dependency management | Unpinned `anthropic` SDK | Pin exact version in requirements.txt at setup time |
| Content/ directory | Missing directory crashes file write | Add `.gitkeep` or `mkdir(exist_ok=True)` before first run |

---

## Sources

- Analysis of existing codebase: `.github/workflows/morning.yml`, `.github/workflows/evening.yml`, `scripts/plan_state.py`, `scripts/push_bark.py`
- Existing architecture patterns in project (stdout/stdin pipe, `sys.exit(1)` on errors, `ensure_ascii=False` convention)
- Domain knowledge: GitHub Actions scheduler behavior, RSS feed fragility patterns, Anthropic SDK versioning history, git-from-CI patterns (HIGH confidence from training data up to August 2025, MEDIUM for specifics — web search unavailable to verify current state)
- Confidence note: Pitfalls 1, 3, 5, 8 are HIGH confidence (structural/architectural, well-established). Pitfall 9 (SDK version numbers) is MEDIUM — verify current Anthropic SDK version at implementation time.
