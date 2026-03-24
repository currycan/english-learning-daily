# Project Research Summary

**Project:** English Learning Daily — v2.0 Website Milestone
**Domain:** Mobile-first static reading/learning website (Astro + GitHub Pages) layered on existing Python content pipeline
**Researched:** 2026-03-24
**Confidence:** HIGH

## Executive Summary

This project adds a static website frontend to an already-functioning Python/GitHub Actions content pipeline. The pipeline generates `content/YYYY-MM-DD.md` files daily; the website consumes them at build time and serves them as a mobile-first reading app on GitHub Pages. The canonical approach — confirmed against official Astro and GitHub documentation — is an Astro 6.x project in a `website/` subdirectory using the Content Collections `glob()` loader with `.passthrough()` schema, deployed via `withastro/action@v3` and `actions/deploy-pages@v4` as a downstream job in the existing `daily-content.yml` workflow. No new secrets, no backend, no client-side framework — the site is 100% static HTML with approximately 30 lines of vanilla JS for dark mode and read-tracking.

The feature set is well-scoped and implementation patterns are all well-documented. Every UI requirement maps to either a native HTML feature (`<details>/<summary>` for collapsibles, CSS custom properties for theming) or a small build-time computation (date-fns calendar grid). The key differentiator — visual read/unread progress on the calendar — is achievable with localStorage and a single `<script is:inline>` block. There are no novel engineering challenges here; the risk is almost entirely in configuration and integration details.

The dominant risk category is CI/CD configuration: four issues (missing `base` URL, `workflow_run` branch restriction, concurrent deploy race condition, and content collections hard-failing on frontmatter-free files) will all cause blocking failures if not addressed in the first phase. All four have clear, well-documented solutions and must be resolved before writing any page component.

## Key Findings

### Recommended Stack

Astro 6.x is the right choice for this project: it is the current stable release, its Content Collections API handles the frontmatter-free existing Markdown files via `z.object({}).passthrough()`, and it deploys to GitHub Pages via the official `withastro/action` without needing a PAT or deploy key. Tailwind CSS 4 integrates via the `@tailwindcss/vite` plugin (the legacy `@astrojs/tailwind` integration is deprecated and must not be used). `date-fns` 4.x runs only at build time for the calendar grid — zero client bytes. The entire client-side JavaScript footprint is approximately 30 lines of vanilla JS split between dark mode and read-tracking.

**Core technologies:**
- Astro 6.x: static site generator and content layer — current stable, native Content Collections, GitHub Pages first-class support
- Tailwind CSS 4 via `@tailwindcss/vite`: utility CSS — replaces deprecated `@astrojs/tailwind`; dark mode via `@custom-variant dark`
- `@tailwindcss/typography`: prose styling for article reading — applies correct line-height and font size without manual CSS
- `date-fns` 4.x: build-time calendar grid generation — tree-shakeable, zero runtime cost
- TypeScript "base" preset: type checking — bundled with Astro, no separate install required
- `withastro/action@v3` + `actions/deploy-pages@v4`: GitHub Pages deployment — uses auto-provided `GITHUB_TOKEN`, no PAT required

**Critical version constraints:**
- Astro 6 requires Node 22+ (GitHub Actions `ubuntu-latest` provides Node 24 — compatible)
- Tailwind 4 requires Astro 5.2+ or 6.x (not earlier)
- Content Collections config file location is `src/content.config.ts` (Astro 5+ location, NOT `src/content/config.ts`)

### Expected Features

The feature set for v2.0 is fully defined and scoped against locked decisions in PROJECT.md (D-01 through D-26). There are no ambiguous "maybe" features.

**Must have (table stakes — all P1 for v2.0):**
- Today's lesson on homepage with recent 5-7 day list — primary use case
- Article text always visible, never collapsible — core reading UX
- Collapsible vocabulary, expressions, and comprehension sections via `<details>` — mobile screen management
- Per-question tap-to-reveal answers (EN + Chinese together in one toggle) — active recall preservation
- Archive calendar with month navigation and tappable content days
- Comfortable mobile typography: 16-18px body, 1.5-1.6 line-height, 44px min tap targets
- Dark/light mode with system auto-follow, manual toggle, localStorage persistence, no flash of wrong theme
- Graceful empty state showing most recent lesson when today's is not yet generated

**Should have (differentiators — all P1 for v2.0):**
- Reading progress via localStorage: auto-mark on lesson page load, no button needed
- Visual read/unread indicators on calendar cells
- Build-time content index via Content Collections — no runtime API calls, no loading spinners

**Defer to v2.x:**
- Previous/next lesson navigation links on lesson pages — convenient but not blocking
- Section collapse state persisted in localStorage — add only if users report friction

**Defer to v3+:**
- Client-side full-text search (Pagefind) — valuable only at 50+ lessons
- Password protection — explicitly deferred in project context

**Anti-features to avoid:**
- "Expand all / Collapse all" button — clutters mobile; per-section `<details>` covers the need
- Explicit "Mark as read" button — auto-mark on page load covers 95% of cases
- Quiz/scoring mode — out of scope; tap-to-reveal is the correct stopping point for B1-B2 reading
- Cross-device sync — requires backend; accept localStorage-only limitation

### Architecture Approach

The architecture is a clean two-layer system: the existing Python pipeline produces `content/*.md` files committed to the repository, and the Astro build consumes them at CI time via the `glob()` loader pointing at `../../content/` from the `website/` subdirectory. The `website/` isolation is not cosmetic — it prevents `node_modules/` from conflicting with the Python `venv/` and keeps Node CI steps cleanly scoped to `working-directory: website`. The critical architectural decision is to add `build-and-deploy` as a downstream job in the existing `daily-content.yml` workflow (using `needs: generate-content`) rather than using a separate `workflow_run`-triggered file — this single decision eliminates three distinct pitfalls.

**Major components:**
1. `src/content.config.ts` — defines `lessons` collection via glob loader at `../../content/`; `.passthrough()` schema for frontmatter-free files
2. `src/lib/parseLesson.ts` — pure TypeScript function; splits raw `body` on `^## ` to produce 4 typed section strings
3. `src/pages/index.astro` — homepage; today's lesson full-width + recent list + graceful empty state fallback
4. `src/pages/lesson/[date].astro` — dynamic static route per date; renders 4 section components with distinct interactivity
5. `src/pages/archive.astro` — calendar grid; static HTML structure + inline script for localStorage read-state injection
6. `src/components/` — `VocabCard`, `ChunkCard`, `QAItem` (one per content type), `CalendarGrid`; all receive pre-parsed strings
7. `src/layouts/Base.astro` — HTML shell with `is:inline` theme detection script in `<head>` before first paint
8. `.github/workflows/daily-content.yml` (modified) — adds `build-and-deploy` job with `needs: generate-content` and `concurrency` group

**State boundaries:** All lesson content is build-time static HTML. Only two concerns are client-side: theme preference (`localStorage.themeOverride`) read in `<head>` before first paint, and read progress (`localStorage.readLessons` array) written on lesson page load and read on archive page load.

### Critical Pitfalls

1. **Missing `base: '/study-all'` in `astro.config.mjs`** — every asset 404s on GitHub Pages; local dev works fine masking the bug. Set `base` and `site` on day one and use `import.meta.env.BASE_URL` for all internal links. Severity: BLOCKING.
2. **Content collections hard-fail on frontmatter-free files** — existing `.md` files have no YAML frontmatter; any required schema field causes `InvalidContentEntryFrontmatterError` on every file. Use `z.object({}).passthrough()` in the collection schema. Severity: BLOCKING.
3. **`workflow_run` trigger only fires on the default branch** — a separate deploy workflow file on a feature branch never fires; impossible to test without merging. Use `needs: generate-content` in the same workflow file. Severity: BLOCKING if using `workflow_run`.
4. **Concurrent deploy race condition** — two overlapping workflow runs produce a non-fast-forward git failure. Add `concurrency: group: github-pages-deploy` to the deploy job. Severity: BLOCKING (intermittent).
5. **Dark mode flash of wrong theme (FOUC)** — Astro bundles scripts externally by default; the theme class reaches `<html>` after first paint. Mark the theme detection script `is:inline` in `<head>`. Severity: Annoying on every page load for dark-mode users.

## Implications for Roadmap

Based on research, the dependency graph and pitfall-to-phase mapping point to a clear 4-phase structure.

### Phase 1: Foundation — Astro Scaffold, CI/CD, Content Loading

**Rationale:** All 4 blocking pitfalls are infrastructure-layer issues that must be resolved before any content can be rendered. A broken foundation that deploys incorrectly wastes all subsequent implementation work. The `base` URL, workflow architecture, content collections schema, and concurrency configuration are pre-requisites for every subsequent phase.

**Delivers:** A deployable (but content-free) Astro site at `https://username.github.io/study-all/` wired into the existing content pipeline; CI builds and deploys on every push to `content/**`.

**Key tasks:** Scaffold Astro 6 in `website/`; configure `astro.config.mjs` with `site`, `base: 'study-all'`, `trailingSlash: 'always'`; write `src/content.config.ts` with `.passthrough()` schema; add `build-and-deploy` job with `needs: generate-content` and `concurrency` group; add `public/.nojekyll`; verify deploy reaches Pages and all routes resolve.

**Avoids:** Missing `base` URL (Pitfall 1), content collections frontmatter failure (Pitfall 2/4), `workflow_run` restriction (Pitfall 3), concurrent deploy race condition (Pitfall 4).

**Research flag:** Standard patterns — skip `research-phase`. All configuration values are documented in official Astro and GitHub Actions docs.

### Phase 2: Lesson Pages and Core Reading UX

**Rationale:** Lesson pages are the dependency root for every other feature — the calendar links to them, the read tracker writes on them, and the homepage references them. They must exist before the archive or homepage can be meaningfully built or tested. The `Base.astro` layout is also created here, and the FOUC-prevention inline script must be correct from the start.

**Delivers:** Fully functional lesson pages at `/lesson/YYYY-MM-DD/` with article always visible, collapsible vocab/expressions/comprehension via `<details>`, per-question tap-to-reveal answers (EN + Chinese together), mobile typography, dark/light mode with no FOUC, and localStorage read tracking.

**Key tasks:** Write `parseLesson.ts` with emoji-aware section splitter (unit-tested against actual `content/2026-03-24.md`, not a synthetic fixture); write `VocabCard`, `ChunkCard`, `QAItem` components; write `Base.astro` with `is:inline` theme detection script; implement dark mode toggle with CSS custom properties; implement localStorage read tracking with `safeGet`/`safeSet` try/catch wrapper.

**Avoids:** FOUC (Pitfall 5 — `is:inline` in `Base.astro`); emoji header parsing bugs (Pitfall 6 — test with real content); localStorage Safari crash (Pitfall 7 — try/catch wrapper from day one).

**Research flag:** Standard patterns — `<details>` collapsibles, FOUC prevention, and localStorage are all well-documented. Skip `research-phase`.

### Phase 3: Homepage with Today's Lesson and Empty State

**Rationale:** Homepage depends on lesson pages existing (it links to them) and on the content index being queryable. The empty state logic — showing most recent lesson when today's is missing — must handle zero-file, one-file, and stale-file edge cases explicitly since these states occur routinely at project inception and after pipeline skips.

**Delivers:** Homepage showing today's lesson full-width (or most recent with "今日课文将在中午更新" label if today's is not yet generated), recent 5-7 day list, and graceful empty state for zero-content edge case.

**Key tasks:** Write `index.astro`; implement 3-state fallback logic (today → most recent → placeholder); derive date from filename `id`, never from client `new Date()`; test with zero, one, and past-date-only content files.

**Avoids:** Single-file homepage build failure (Pitfall 10 — explicit fallback chain); timezone date errors (derive date from filename, not from `new Date()`).

**Research flag:** Standard patterns — skip `research-phase`.

### Phase 4: Archive Calendar with Read/Unread Indicators

**Rationale:** Calendar is the most complex client-side component and depends on lesson pages existing (cells link to them) and localStorage read tracking being in place (Phase 2). Month navigation introduces the only stateful vanilla-JS interaction in the project; the stale event listener pitfall is easy to introduce and silent until tested.

**Delivers:** Calendar archive at `/archive/` with month grid, tappable content days, greyed empty days, month navigation arrows, and read/unread visual state loaded from localStorage.

**Key tasks:** Write `CalendarGrid.astro`; implement build-time month grid via `date-fns` (`eachDayOfInterval`, `startOfMonth`, `endOfMonth`, `getDay`); implement month navigation with event delegation on container (not per-cell); add `is:inline` script for localStorage read-state injection; test 5+ month navigations for listener accumulation.

**Avoids:** Calendar stale event listeners (Pitfall 8 — event delegation, pure `renderCalendar()` function replacing `innerHTML` safely); localStorage Safari crash (same `safeGet` wrapper from Phase 2).

**Research flag:** Standard patterns. Flag the event delegation implementation for code review — the stale listener bug is easy to introduce and only surfaces after several month navigations.

### Phase Ordering Rationale

- Phase 1 first because all 4 blocking pitfalls are infrastructure-layer issues; any page built on a broken foundation must be retested after fixes.
- Phase 2 before Phase 3 because the homepage links to lesson pages — those routes must exist for link testing to be meaningful.
- Phase 2 before Phase 4 because the calendar's read state depends on localStorage writes that happen on lesson pages.
- Phase 3 before Phase 4 because the homepage and calendar share the same sorted collection query — validating it in Phase 3 reduces risk in Phase 4.

### Research Flags

Phases likely needing deeper research during planning:
- None. All four phases use well-documented, official patterns with multiple high-confidence sources. No third-party integrations with sparse documentation, no novel APIs.

Phases with standard patterns (skip `research-phase`):
- **All phases:** Astro Content Collections, GitHub Pages deployment, Tailwind 4, `<details>/<summary>`, localStorage, and `date-fns` calendar all have official documentation and recent community examples confirming correct usage.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | All core choices verified against official Astro 6, Tailwind 4, and GitHub Actions docs. One MEDIUM item: Astro 6 stable release confirmed via a third-party blog post, not official Astro release notes — but version trajectory is confirmed in Astro's own year-in-review. |
| Features | HIGH | All features map directly to locked decisions in PROJECT.md (D-01 through D-26). UX patterns verified via MDN, WCAG 2.5.5, and multiple community sources. |
| Architecture | HIGH | All architectural decisions verified against official Astro docs and GitHub Actions docs. Anti-patterns backed by concrete GitHub issues as evidence. |
| Pitfalls | HIGH | All 4 blocking pitfalls have official documentation as source. Moderate pitfalls backed by MDN, browser vendor docs, and community bug reports with reproducible examples. |

**Overall confidence:** HIGH

### Gaps to Address

- **Emoji section header parsing correctness:** The `parseLesson.ts` unit tests must use `content/2026-03-24.md` as the literal input, not a synthetic test fixture with ASCII-only headers. This is a validation gap, not a knowledge gap — the implementation approach is clear, but correctness must be confirmed against real content before lesson pages go live.
- **`trailingSlash` behavior on GitHub Pages:** The recommendation is `trailingSlash: 'always'` + `build.format: 'directory'`, but redirect behavior for slash-less URLs should be verified on the actual deployed site in Phase 1, not assumed from documentation alone.
- **Astro 6 `src/content.config.ts` file location:** Astro 5+ moved the config file location. Confirm the exact path during scaffold — a misplaced config silently produces an empty collection with no build error.

## Sources

### Primary (HIGH confidence)
- [Astro GitHub Pages Deploy Guide](https://docs.astro.build/en/guides/deploy/github/) — base, site, withastro/action, permissions, trailingSlash
- [Astro Content Collections Docs](https://docs.astro.build/en/guides/content-collections/) — glob loader, getCollection, .passthrough() schema
- [Astro Configuration Reference](https://docs.astro.build/en/reference/configuration-reference/) — site, base, trailingSlash, build.format options
- [withastro/action GitHub repo](https://github.com/withastro/action) — v3 current, required permissions
- [Tailwind CSS Astro Install Guide](https://tailwindcss.com/docs/installation/framework-guides/astro) — @tailwindcss/vite plugin setup
- [Astro 5.2 Release Blog](https://astro.build/blog/astro-520/) — Tailwind 4 support confirmed
- [Astro 2025 Year in Review](https://astro.build/blog/year-in-review-2025/) — v6 version trajectory
- [GitHub Actions Events Docs](https://docs.github.com/actions/using-workflows/events-that-trigger-workflows) — workflow_run default-branch restriction
- [Astro dark mode docs tutorial](https://docs.astro.build/en/tutorial/6-islands/2/) — is:inline canonical approach
- [MDN: Window localStorage](https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage)
- [MDN: details/summary element](https://developer.mozilla.org/en-US/blog/html-details-exclusive-accordions/)
- [WCAG 2.5.5 — target size](https://digital.gov/guides/mobile-principles/tap-targets) — 44px tap target requirement

### Secondary (MEDIUM confidence)
- [Southwell Media: Astro 6 Stable Release (2026)](https://www.southwellmedia.com/blog/astro-6-stable-release) — Node 22 requirement, breaking changes list
- [myles.garden: Building a Calendar Interface in Astro (September 2025)](https://myles.garden/2025/09/21/astro-calendar) — date-fns build-time calendar pattern
- [axellarsson.com: Astro FOUC prevention](https://axellarsson.com/blog/astrojs-prevent-dark-mode-flicker/) — is:inline confirmed as canonical fix
- [lossless.group: Astro Collections with messy frontmatter](https://www.lossless.group/learn-with/issue-resolution/getting-astro-collections-to-work-on-messy-frontmatter) — .passthrough() pattern
- [mattburke.dev: Safari Private Browsing localStorage](https://mattburke.dev/dom-exception-22-quota-exceeded-on-safari-private-browsing-with-localstorage/) — QuotaExceededError confirmed
- [GitHub Community: workflow_run default branch restriction](https://github.com/orgs/community/discussions/72097)
- [GitHub issue tket#63: race condition on gh-pages](https://github.com/CQCL/tket/issues/63) — concurrent deploy failure example
- [oneuptime.com: GitHub Actions concurrency control (2026-01-25)](https://oneuptime.com/blog/post/2026-01-25-github-actions-concurrency-control/view) — concurrency group patterns

### Project context
- `.planning/website-CONTEXT.md` — decisions D-01 through D-26 (locked)
- `.planning/PROJECT.md` — v2.0 Active requirements, Out of Scope constraints
- `content/2026-03-24.md` — actual Markdown format driving parser and display decisions

---
*Research completed: 2026-03-24*
*Ready for roadmap: yes*
