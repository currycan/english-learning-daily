# Pitfalls Research

**Domain:** Astro static site added to existing Python + GitHub Actions content pipeline
**Researched:** 2026-03-24
**Confidence:** HIGH (GitHub Actions pitfalls verified via official community; Astro pitfalls verified via official docs + GitHub issues; localStorage/FOUC patterns verified via MDN + community)

---

## Critical Pitfalls

Mistakes that cause blocking failures or require rewrites.

---

### Pitfall 1: Missing `base` in `astro.config.mjs` — Every Asset 404s on GitHub Pages

**What goes wrong:**
GitHub Pages serves repos at `https://username.github.io/repo-name/` (not the root). Without `base: '/study-all'` in `astro.config.mjs`, every generated `<script src="/...">`, `<link href="/...">`, and `<img src="/...">` resolves to `username.github.io/assets/...` instead of `username.github.io/study-all/assets/...`. The site renders a blank page with 404s in the console.

**Why it happens:**
Astro defaults to `base: '/'`. Developers test locally (where `/` is correct) and only discover the issue after the first deploy. The GitHub Pages URL structure is non-obvious when the repo is not a user/org site.

**How to avoid:**
Set `base: '/study-all'` (repo name) and `site: 'https://username.github.io'` in `astro.config.mjs` on day one — before writing any routes. Use `import.meta.env.BASE_URL` instead of hardcoded `/` in all internal `<a href>`, `<img src>`, and `fetch()` calls. Astro's built-in `<Image>` and `<a>` components handle `base` automatically; raw HTML `<a href="/archive">` does not.

**Warning signs:**
- Local `npm run preview` works but deployed site shows blank page
- Browser DevTools shows 404s for `/assets/index-*.js`
- Works at `username.github.io/study-all/` but every link leads to 404

**Phase to address:** Phase 1 (Astro scaffold + GitHub Pages deployment). Fix before writing any content routes.

**Severity:** BLOCKING

---

### Pitfall 2: `workflow_run` Trigger Only Fires on the Default Branch

**What goes wrong:**
If the Astro build workflow uses `workflow_run` to trigger after `daily-content.yml` completes, the trigger workflow file must exist on the **default branch** (master) for the event to fire. A workflow file added on a feature branch and not yet merged will never trigger — making it impossible to test the `workflow_run` integration without merging first.

**Why it happens:**
This is a documented GitHub limitation: `workflow_run` evaluates the triggering workflow against the workflow file on the default branch only. There is no workaround for testing on feature branches; this is a hard platform constraint as of 2026.

**How to avoid:**
Do not use a separate `workflow_run`-triggered workflow file. Instead, add the Astro build as a **downstream `job`** inside the existing `daily-content.yml` using `needs: generate-content`. This:
- Avoids the `workflow_run` restriction entirely
- Runs in the same workflow file (always on default branch)
- Naturally skips the deploy if content generation was skipped (idempotency guard already exits 0 when file exists)
- Is testable via `workflow_dispatch` on any branch

Concretely, add `build-and-deploy: needs: [generate-content]` as a second job in `daily-content.yml`.

**Warning signs:**
- Separate deploy workflow file added but never fires after content commits
- No deploy runs visible in Actions despite content commits landing

**Phase to address:** Phase 1 (CI/CD architecture). Decision must be made before writing the workflow.

**Severity:** BLOCKING if using `workflow_run`; fully avoidable by using `needs:` in the same file.

---

### Pitfall 3: Race Condition — Content Commit Triggers Deploy While Previous Deploy Is In Progress

**What goes wrong:**
Two content commits arriving in quick succession (e.g., manual rerun + scheduled run on the same day, or the idempotency guard exits early but a subsequent `workflow_dispatch` runs) can trigger two deploy jobs concurrently. Both jobs try to push to the `gh-pages` branch. The second push fails with a non-fast-forward error, leaving the site in a partially deployed state.

**Why it happens:**
GitHub Pages deployments via `peaceiris/actions-gh-pages` or the official `actions/deploy-pages` action push to a branch or upload an artifact. Concurrent pushes to the same branch fail on git's non-fast-forward check. Even if only one content commit triggers a deploy, the GitHub Actions queue can run two instances.

**How to avoid:**
Add a `concurrency` group to the deploy job:
```yaml
concurrency:
  group: github-pages-deploy
  cancel-in-progress: false
```
`cancel-in-progress: false` queues the second deploy rather than cancelling it, ensuring the latest content always lands. Use `cancel-in-progress: true` only if you prefer to always deploy the newest commit and discard intermediate builds (acceptable here since content is idempotent).

**Warning signs:**
- Intermittent deploy job failures with `rejected: non-fast-forward` git errors
- Site sometimes shows yesterday's content after a manual rerun

**Phase to address:** Phase 1 (CI/CD). Add `concurrency:` at the same time as the deploy job.

**Severity:** BLOCKING (intermittent failures under concurrent runs)

---

### Pitfall 4: Existing Markdown Files Have No Frontmatter — Content Collections Will Hard-Fail

**What goes wrong:**
Astro's content collections (`getCollection()`) require files in `src/content/` to conform to a Zod schema. The existing `content/YYYY-MM-DD.md` files have **no frontmatter at all** — they start directly with `## 📖 文章 / Article`. If these files are placed in a content collection with any required fields (e.g., `title`, `date`), Astro throws a build-time `InvalidContentEntryFrontmatterError` for every file and the build fails completely.

**Why it happens:**
The existing pipeline was designed to produce human-readable Markdown with zero metadata overhead. Content collections assume frontmatter-driven content. The mismatch is absolute: zero frontmatter vs. required schema fields.

**How to avoid:**
Two valid paths:
1. **Use `import.meta.glob()` instead of content collections.** Glob-import the raw Markdown files, parse the filename for the date, and parse the body manually. No frontmatter required. This is simpler for this project's structure.
2. **Inject frontmatter in the CI build step.** Before Astro builds, a script generates a `src/content-index.json` (already planned per D-05) with `{date, title, path}` entries. Astro reads this JSON index instead of the raw `.md` files directly. Lesson pages then fetch the raw `.md` via `import.meta.glob()` for rendering.

Do not use content collections with the raw files as-is without a schema that uses `z.object({}).passthrough()` with all fields optional.

**Warning signs:**
- `InvalidContentEntryFrontmatterError` or `MarkdownContentSchemaValidationError` on first `astro build`
- Build succeeds locally but fails when content files are present

**Phase to address:** Phase 1 (Astro scaffold). Decide the content-loading strategy before building any pages.

**Severity:** BLOCKING

---

### Pitfall 5: Dark Mode Flash of Wrong Theme (FOUC) on First Load

**What goes wrong:**
The browser renders the page with the default (light) theme, then a client-side script reads `localStorage` and applies the `dark` class to `<html>`. This causes a visible flash from light to dark on every page load when the user's preference is dark mode. On mobile (the primary use case for this project), the flash is particularly jarring.

**Why it happens:**
Astro bundles scripts as external files by default. External scripts load asynchronously, after the HTML is painted. By the time the theme script runs and adds `class="dark"` to `<html>`, the browser has already rendered the page without it.

**How to avoid:**
Place the theme-detection script **inline in `<head>`** using Astro's `is:inline` directive. This makes the script execute synchronously before the browser paints:
```astro
<head>
  <script is:inline>
    const stored = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    if (stored === 'dark' || (!stored && prefersDark)) {
      document.documentElement.classList.add('dark');
    }
  </script>
</head>
```
`is:inline` tells Astro not to bundle this script — it remains inline and runs immediately. Without `is:inline`, Astro moves it to an external bundle and the FOUC occurs.

**Warning signs:**
- White flash before dark theme applies on page load
- Theme class appears in DevTools only after `DOMContentLoaded`
- Works in production preview but not noticed in dev (Vite HMR masks it)

**Phase to address:** Phase 2 or whichever phase implements dark mode toggle.

**Severity:** Annoying (not blocking, but visible on every page load for dark-mode users)

---

## Moderate Pitfalls

---

### Pitfall 6: Emoji in Section Headers Break Naive Regex-Based Parsing

**What goes wrong:**
The content files use headers like `## 📖 文章 / Article`. A naive regex like `/^## (.+)/` or a split on `\n## ` will include the emoji in the section key, making comparisons like `section.startsWith('📖')` fail due to encoding inconsistencies. Multi-byte emoji sequences (`📖` is U+1F4D6, a 4-byte UTF-8 sequence) interact badly with JavaScript's `string.length` and substring operations — e.g., `header.slice(3)` after removing `## ` gives `📖 文章 / Article`, but `header.slice(0, 1)` gives a surrogate pair, not `📖`.

**Why it happens:**
JavaScript strings are UTF-16 internally. Emoji outside the Basic Multilingual Plane (most colored emoji) are two code units ("surrogate pairs"). `'📖'.length === 2`, not 1. Operations that assume `length === code points` will slice mid-codepoint.

**How to avoid:**
Use Astro's built-in remark/rehype pipeline to parse the Markdown into an AST. Extract sections from the AST by heading level and text content, not via raw string splitting. To match section types, compare the heading text after stripping whitespace with exact emoji literals (use copy-paste, not escape codes): `heading.includes('📖')` is safe; `heading.charCodeAt(0) === 0xD83D` is fragile. If raw string splitting is unavoidable, split on `\n## ` and test with the actual production file `content/2026-03-24.md` in unit tests.

**Warning signs:**
- Section parsing works for ASCII headers but silently produces empty sections for emoji headers
- `slice()` or `substring()` on a heading containing emoji returns garbled text
- Unit tests pass with `## Title` but fail with `## 📖 Title`

**Phase to address:** Whichever phase implements the lesson page content renderer.

**Severity:** Moderate (silent wrong output, not a crash)

---

### Pitfall 7: `localStorage` Throws in Safari Private Browsing and Quota Exceeded

**What goes wrong:**
Reading progress and dark-mode preference both use `localStorage`. In Safari Private Browsing mode, `localStorage.setItem()` throws `QuotaExceededError` even when the storage appears empty. If the code calls `localStorage.setItem()` without a try/catch, the entire lesson page JavaScript crashes at the storage call, breaking the tap-to-reveal answer functionality and dark mode toggle.

**Why it happens:**
Safari Private Mode historically set a 0-byte quota for `localStorage`, causing every write to throw. Modern Safari (iOS 17+) has improved this but still shows inconsistent behavior. `JSON.parse(localStorage.getItem('read_lessons'))` also throws if the stored value is corrupted or `null` — which happens if a previous session failed mid-write.

**How to avoid:**
Wrap all `localStorage` access in a `safeStorage` utility:
```javascript
function safeGet(key, fallback) {
  try { return JSON.parse(localStorage.getItem(key)) ?? fallback; }
  catch { return fallback; }
}
function safeSet(key, value) {
  try { localStorage.setItem(key, JSON.stringify(value)); }
  catch { /* storage unavailable — degrade gracefully */ }
}
```
Design the UI so it **works correctly without localStorage** — reading progress simply resets, dark mode follows the system preference. Storage is an enhancement, not a requirement.

**Warning signs:**
- Tap-to-reveal answers stop working in private browsing
- Dark mode toggle works once but resets on reload in Safari
- Console shows `QuotaExceededError` or `SecurityError`

**Phase to address:** Any phase implementing localStorage (dark mode toggle, reading progress).

**Severity:** Moderate (breaks for Safari Private Browsing users; common mobile use case)

---

### Pitfall 8: Calendar Built With Pure Vanilla JS — State Synchronization Complexity

**What goes wrong:**
A calendar that shows month navigation, marks days with content, and marks read/unread days needs to: (1) render the correct month grid, (2) re-render when the user navigates months, (3) read the localStorage state and mark read cells. Without a reactive framework, all three concerns are manually coordinated with `innerHTML` resets and `addEventListener` cleanup. Re-renders frequently leave stale event listeners attached to removed DOM nodes (memory leak) or duplicate event listeners (double-fire bugs).

**Why it happens:**
Each time the month changes, developers often `innerHTML = ''` and re-render, forgetting to remove event listeners from the old nodes before clearing. Or they add a new `addEventListener` on each render without checking if one already exists.

**How to avoid:**
Use **event delegation** on the calendar container instead of per-cell listeners: one `addEventListener('click', ...)` on `#calendar-grid` checks `event.target.dataset.date` to route the click. This survives `innerHTML` rewrites and requires no cleanup. For month navigation, derive the entire calendar state from a single `currentMonth` variable and replace `innerHTML` on each navigation — with event delegation this is safe. Keep the calendar rendering as a pure function: `renderCalendar(year, month, contentDates, readDates) => HTML string`.

**Warning signs:**
- Clicking a date triggers the handler multiple times (N times after N month navigations)
- Memory profile shows growing event listener count as user navigates months
- Calendar cells stop responding to clicks after the 3rd month navigation

**Phase to address:** Whichever phase implements the archive/calendar view.

**Severity:** Moderate (correct on first load; degrades with user interaction)

---

### Pitfall 9: Astro `trailingSlash` Mismatch — Links Work Locally, 404 on GitHub Pages

**What goes wrong:**
Astro defaults to `trailingSlash: 'ignore'`, generating pages as both `/lesson/2026-03-24` and `/lesson/2026-03-24/`. GitHub Pages serves static files: a request to `/lesson/2026-03-24` (no slash) returns 404 if the file is `lesson/2026-03-24/index.html` (Astro's default directory output format). Conversely, if set to `trailingSlash: 'never'`, Astro generates `lesson/2026-03-24.html` but GitHub Pages does not serve `2026-03-24.html` without the extension in the URL — it returns 404.

**Why it happens:**
GitHub Pages serves files at exact paths. Astro's `trailingSlash: 'always'` generates `lesson/2026-03-24/index.html`. GitHub Pages serves this at `lesson/2026-03-24/` (with trailing slash). Links to `lesson/2026-03-24` without the slash work because GitHub Pages issues a redirect — but this adds a round-trip on mobile networks.

**How to avoid:**
Set `trailingSlash: 'always'` and `build.format: 'directory'` in `astro.config.mjs`. Always use trailing slashes in all internal `<a href>` links. Test the deployed site by navigating links rather than just typing URLs directly.

**Warning signs:**
- Direct URL entry to lesson pages returns 404
- Links work but browser address bar shows a redirect (302) before landing
- 404 appears on deep links shared via messaging apps

**Phase to address:** Phase 1 (Astro scaffold configuration).

**Severity:** Moderate (404s on direct navigation and shared links)

---

### Pitfall 10: Only One Content File Exists — "Today's Lesson" Logic Breaks

**What goes wrong:**
The homepage shows "today's lesson" by finding a file matching today's Beijing date. When only one file exists (the current state: `content/2026-03-24.md`), the logic works. After two weeks of production use, the "today" lookup may find no file if the daily pipeline was skipped (scheduler failure, API rate limit). Falling through to `undefined` then accessing `.title` throws, breaking the entire homepage build.

**Why it happens:**
Build-time code that assumes "at least one file exists today" doesn't hold at project inception (only 1 file), on weekends if the user pauses the pipeline, or after a scheduler failure. The build fails instead of degrading gracefully.

**How to avoid:**
Design the homepage content logic with explicit fallbacks:
1. If today's file exists → show it
2. Else → show the most recent file with a "Last available lesson" label
3. If no files at all → render a placeholder ("No lessons yet")

Test this explicitly by running `astro build` with `content/` containing: (a) zero files, (b) one file, (c) a file from a past date only.

**Warning signs:**
- `astro build` fails with `Cannot read properties of undefined` on the homepage
- Build works in CI but fails locally if `content/` is empty

**Phase to address:** Phase 2 (homepage implementation). Add the graceful fallback as a success criterion.

**Severity:** Moderate (build breaks; users see error page)

---

## Technical Debt Patterns

Shortcuts that seem reasonable but create long-term problems.

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Hardcode `base: '/study-all'` in multiple places | Quick | Breaks if repo is renamed; must update everywhere | Never — use `import.meta.env.BASE_URL` instead |
| Parse Markdown via raw string splitting instead of AST | Simpler code | Breaks silently when content format drifts; emoji and multiline headers cause bugs | Only if content format is tested with a snapshot test per content change |
| Store `read_lessons` as a plain string instead of JSON array | Simpler | `JSON.parse` fails if corrupted; must handle `null` | Never — always parse/serialize with try/catch |
| Inline all CSS in `<style>` tags per component | Faster initial setup | No shared design tokens; dark mode requires duplicating color overrides everywhere | Early prototyping only; extract CSS variables before dark mode implementation |
| Use `workflow_run` trigger for Astro build | Decoupled workflow files | Fails to fire from non-default branches; impossible to test without merging | Never — use `needs:` in the same workflow file |

---

## Integration Gotchas

Common mistakes when connecting to the existing pipeline.

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| GitHub Pages + existing workflow | Add a new separate workflow file for deploy | Add `build-and-deploy` job to existing `daily-content.yml` with `needs: generate-content` |
| Content files → Astro build | Place raw `content/*.md` files in `src/content/` for getCollection() | Use `import.meta.glob('../content/*.md')` or generate a JSON index in CI; do not use content collections with frontmatter-free files |
| GitHub Pages `base` path | Test locally and assume `/` works everywhere | Set `base` in `astro.config.mjs` from day one; use `import.meta.env.BASE_URL` throughout |
| Beijing-timezone dates | Use `new Date().toISOString().slice(0,10)` (returns UTC date) | Extract date from filename (`2026-03-24.md` → `'2026-03-24'`); never derive from `new Date()` on the client |
| Dark mode localStorage | Read/write localStorage directly | Always wrap in try/catch; design UI to work without storage |
| CI concurrent deploys | No concurrency control | Add `concurrency: group: github-pages-deploy` to the deploy job |

---

## Performance Traps

Patterns that work at small scale but create problems.

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Loading all Markdown files at runtime via fetch | Works for 10 files; slow for 365 | Generate a JSON index at build time listing all lesson dates/titles; serve as a static asset | ~50+ files or slow mobile connections |
| Rendering all calendar months in the DOM at once | Fast to implement | Render only the visible month; use event delegation; replace `innerHTML` on navigation | Visual lag on lower-end phones at 12+ months |
| Reading localStorage on every component mount separately | Simpler per-component | Read once on page load into a module-level variable; components read from the variable | Only a DX issue; not a scale concern |

---

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| Injecting Markdown body as raw `innerHTML` | XSS if AI-generated content ever includes script tags | Use Astro's built-in Markdown renderer (outputs sanitized HTML); never `innerHTML = markdownBody` |
| Exposing `GEMINI_API_KEY` in Astro build | Key leaked in bundle | API key is server-side only; Astro frontend never needs it; keep in GitHub Secrets |
| GitHub Pages set to public by default | Content publicly readable | Explicitly decided (D-25); document the decision; add access control as a named deferred feature |

---

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Collapsible sections default to open | Defeats the purpose; overwhelming on mobile | Default all three non-article sections to collapsed; `<details>` element handles this without JS |
| Dark mode toggle not persisted on navigation | User re-toggles on every page | Apply theme from localStorage in `<head is:inline>` on every page, not just the page with the toggle button |
| Calendar with no visual distinction for unread vs read | Reading progress feature appears broken | Use a distinct color/indicator for read cells from day one; do not ship the calendar without the read state wired up |
| "Today's lesson" missing because pipeline skipped | User opens site and sees nothing | Always fall back to most recent available lesson with a clear date label |
| Tap-to-reveal answers reveal all answers at once with no reset | User accidentally sees all answers | Implement per-question reveal; add a "Hide answer" toggle after reveal |

---

## "Looks Done But Isn't" Checklist

- [ ] **GitHub Pages base URL:** Local `npm run dev` works, but have you verified `/study-all/lesson/2026-03-24/` works on the deployed site?
- [ ] **Dark mode:** Does the theme persist on page navigation (not just on the page with the toggle)?
- [ ] **FOUC prevention:** Is the theme script `is:inline`? Verify by disabling JS — is the default theme correct?
- [ ] **Concurrency:** Have you tested what happens when `daily-content.yml` is triggered twice in quick succession?
- [ ] **Empty content dir:** Does `astro build` succeed when `content/` is empty or has only one old file?
- [ ] **Safari private browsing:** Does the lesson page work (answers reveal, no JS crash) with DevTools in private mode?
- [ ] **Calendar event listeners:** Navigate forward 5 months, then back, then click a date — does it fire once or multiple times?
- [ ] **Emoji section headers:** Test section parsing with `content/2026-03-24.md` specifically — not with a synthetic `## Section` header.
- [ ] **Trailing slash:** Navigate to a lesson URL by typing it without a trailing slash — does it work?
- [ ] **Idempotency guard + deploy skip:** When today's content already exists and CI exits early, does the deploy job skip correctly (not re-deploy an unchanged build)?

---

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Wrong `base` URL deployed | LOW | Update `astro.config.mjs`, push, rebuild |
| `workflow_run` never fires | LOW | Migrate to `needs:` in same workflow file; merge to master |
| Race condition corrupted gh-pages | LOW | Add `concurrency:`, manually trigger deploy |
| Content collections schema fail on all files | MEDIUM | Switch to `import.meta.glob()` approach; rewrite content-loading code |
| FOUC shipped to production | LOW | Add `is:inline` script to `<head>`; redeploy |
| Calendar stale event listeners | MEDIUM | Refactor to event delegation pattern; test all month navigation paths |
| localStorage crash in Safari | LOW | Add try/catch wrapper; redeploy |

---

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Severity | Verification |
|---------|------------------|----------|--------------|
| Missing `base` in astro.config.mjs | Phase 1 — Astro scaffold | BLOCKING | Deploy to Pages and navigate all routes from a clean browser |
| `workflow_run` default-branch restriction | Phase 1 — CI architecture | BLOCKING | Use `needs:` in same workflow; test with workflow_dispatch |
| Concurrent deploy race condition | Phase 1 — CI architecture | BLOCKING | Add concurrency group; trigger workflow twice, verify second queues |
| No frontmatter — content collections fail | Phase 1 — Astro scaffold | BLOCKING | Run `astro build` with actual `content/` files before writing any pages |
| Dark mode FOUC | Phase 2 — Dark mode toggle | Annoying | Load page with dark preference stored; verify no flash |
| Emoji header parsing | Lesson page phase | Moderate | Unit test parser with `content/2026-03-24.md` as input |
| localStorage Safari crash | Any localStorage phase | Moderate | Test in Safari private browsing; verify no JS errors |
| Calendar stale event listeners | Archive/calendar phase | Moderate | Navigate 5+ months and verify single-fire click |
| trailingSlash 404 | Phase 1 — Astro scaffold | Moderate | Type lesson URL without trailing slash; verify no 404 |
| Single-file homepage failure | Homepage phase | Moderate | Run `astro build` with zero and one content file |

---

## Sources

- [Astro GitHub Pages deployment guide](https://docs.astro.build/en/guides/deploy/github/) — base, site, trailingSlash configuration
- [Astro GitHub issue #7616 — custom 404 and trailing slash](https://github.com/withastro/astro/issues/7616) — confirmed trailing slash edge cases on Pages
- [GitHub Community — workflow_run default branch restriction](https://github.com/orgs/community/discussions/72097) — confirmed `workflow_run` only fires on default branch
- [GitHub Actions concurrency control (oneuptime.com, 2026-01-25)](https://oneuptime.com/blog/post/2026-01-25-github-actions-concurrency-control/view) — concurrency group patterns
- [GitHub tket issue #63 — race condition on gh-pages](https://github.com/CQCL/tket/issues/63) — concrete example of non-fast-forward failure
- [Astro FOUC prevention — axellarsson.com](https://axellarsson.com/blog/astrojs-prevent-dark-mode-flicker/) — `is:inline` pattern verified
- [astro-fouc-killer GitHub repo](https://github.com/avgvstvs96/astro-fouc-killer) — confirms `is:inline` is the canonical solution
- [Astro dark mode docs tutorial](https://docs.astro.build/en/tutorial/6-islands/2/) — official `is:inline` approach
- [Astro content collections — InvalidContentEntryFrontmatterError](https://docs.astro.build/en/reference/errors/invalid-content-entry-frontmatter-error/) — confirmed hard build failure on schema mismatch
- [Getting Astro Collections to Work on Messy Frontmatter — lossless.group](https://www.lossless.group/learn-with/issue-resolution/getting-astro-collections-to-work-on-messy-frontmatter) — `.passthrough()` pattern
- [Safari Private Browsing localStorage — mattburke.dev](https://mattburke.dev/dom-exception-22-quota-exceeded-on-safari-private-browsing-with-localstorage/) — QuotaExceededError confirmed
- [MDN Storage quotas and eviction criteria](https://developer.mozilla.org/en-US/docs/Web/API/Storage_API/Storage_quotas_and_eviction_criteria) — localStorage limits
- [Fail-safe localStorage pattern — dev-tips.com](https://dev-tips.com/javascript/fail-safe-localstorage-sessionstorage-in-javascript) — try/catch wrapper pattern
- [Avoiding the Trailing Slash Tax — justoffbyone.com](https://justoffbyone.com/posts/trailing-slash-tax/) — trailingSlash + GitHub Pages interaction
- [Vanilla Astro, No Framework Needed — telerik.com](https://www.telerik.com/blogs/vanilla-astro-no-framework-needed) — event delegation recommendation for complex vanilla JS

---
*Pitfalls research for: Astro static site added to Python + GitHub Actions content pipeline*
*Researched: 2026-03-24*
