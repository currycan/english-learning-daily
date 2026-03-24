# Roadmap: English Daily Content

## Milestones

- ✅ **v1.0 MVP** — Phases 1-3 (shipped 2026-03-23)
- ✅ **v1.1 Dual AI Provider** — Phases 4-6 (shipped 2026-03-23)
- ✅ **v1.2 Third-Party Claude API** — Phases 7-8 (shipped 2026-03-23)
- ✅ **v1.3 Gemini Migration** — Phase 01 (shipped 2026-03-24)
- 🚧 **v2.0 学习网站** — Phases 02-05 (in progress)

## Phases

<details>
<summary>✅ v1.0 MVP (Phases 1-3) — SHIPPED 2026-03-23</summary>

- [x] Phase 1: Foundation (2/2 plans) — completed 2026-03-22
- [x] Phase 2: RSS Fetch (2/2 plans) — completed 2026-03-22
- [x] Phase 3: AI Pipeline (3/3 plans) — completed 2026-03-23

Full archive: `.planning/milestones/v1.0-ROADMAP.md`

</details>

<details>
<summary>✅ v1.1 Dual AI Provider (Phases 4-6) — SHIPPED 2026-03-23</summary>

- [x] Phase 4: Provider Abstraction + OpenAI Integration (2/2 plans) — completed 2026-03-23
- [x] Phase 5: Fallback Logic (1/1 plan) — completed 2026-03-23
- [x] Phase 6: AI Provider Documentation (2/2 plans) — completed 2026-03-23

Full archive: `.planning/milestones/v1.1-ROADMAP.md`

</details>

<details>
<summary>✅ v1.2 Third-Party Claude API (Phases 7-8) — SHIPPED 2026-03-23</summary>

- [x] Phase 7: Custom Endpoint Implementation (3/3 plans) — completed 2026-03-23
- [x] Phase 8: Third-Party Provider Documentation (1/1 plan) — completed 2026-03-23

Full archive: `.planning/milestones/v1.2-ROADMAP.md`

</details>

<details>
<summary>✅ v1.3 Gemini Migration (Phase 01) — SHIPPED 2026-03-24</summary>

- [x] Phase 01: Gemini Migration (2/2 plans) — completed 2026-03-24

Full archive: `.planning/milestones/v1.3-ROADMAP.md`

</details>

### 🚧 v2.0 学习网站 (In Progress)

**Milestone Goal:** Build a static Astro website on GitHub Pages that renders daily Markdown lessons as a mobile-first reading experience accessible anywhere.

#### Phase Summary Checklist

- [x] **Phase 02: Astro Foundation** — Scaffold Astro site wired into CI/CD with content index loading from existing Markdown files (completed 2026-03-24)
- [ ] **Phase 03: Lesson Reading Experience** — Homepage and lesson pages with full reading UX: collapsible sections, tap-to-reveal answers, mobile typography
- [ ] **Phase 04: Archive Calendar** — Calendar view with month navigation, tappable lesson days, and localStorage read/unread indicators
- [ ] **Phase 05: Theme & Polish** — Dark/light mode with system auto-follow, manual toggle, persistence, and FOUC-free page load

## Phase Details

### Phase 02: Astro Foundation
**Goal**: Users can access a live Astro site on GitHub Pages that auto-deploys whenever new lesson content is committed
**Depends on**: Phase 01 (existing content pipeline producing `content/*.md`)
**Requirements**: SITE-01, SITE-02, SITE-03, SITE-04
**Success Criteria** (what must be TRUE):
  1. User can open `https://<username>.github.io/study-all/` in a browser and see an Astro-generated page
  2. Pushing a new `content/YYYY-MM-DD.md` file triggers a build-and-deploy that completes without errors
  3. The build reads all `content/*.md` files at build time with no runtime API calls and no frontmatter errors
  4. The `website/` directory is isolated from Python scripts and the CI build only runs Node steps inside that directory
**Plans:** 2/2 plans complete
Plans:
- [x] 02-01-PLAN.md — Scaffold Astro project with Tailwind 4, Content Collections, lesson list homepage, and stub lesson pages
- [x] 02-02-PLAN.md — Add build-and-deploy CI/CD job to daily-content.yml and verify live GitHub Pages deployment

### Phase 03: Lesson Reading Experience
**Goal**: Users can read any lesson in full with structured, collapsible exercise sections and tap-to-reveal answers on mobile
**Depends on**: Phase 02
**Requirements**: LESS-01, LESS-02, LESS-03, LESS-04, LESS-05, LESS-06, LESS-07, LESS-08, LESS-09
**Success Criteria** (what must be TRUE):
  1. User opens the homepage and sees today's lesson displayed; if today's lesson is not yet committed, the most recent lesson is shown with a "今日课文将在中午更新" label
  2. Homepage lists the last 5-7 lessons below the featured lesson, each linking to its lesson page
  3. User opens any lesson page and reads the full article text without any interaction required
  4. User can tap the vocabulary, chunking expressions, and comprehension sections independently to expand or collapse each one
  5. User can tap any individual comprehension question to reveal both the English answer and Chinese translation
  6. All text and tap targets on lesson pages are comfortably usable on a phone (body text at least 16px, tap targets at least 44px)
**Plans:** 2 plans
Plans:
- [x] 02-01-PLAN.md — Scaffold Astro project with Tailwind 4, Content Collections, lesson list homepage, and stub lesson pages
- [ ] 02-02-PLAN.md — Add build-and-deploy CI/CD job to daily-content.yml and verify live GitHub Pages deployment
**UI hint**: yes

### Phase 04: Archive Calendar
**Goal**: Users can browse all lessons by date on a calendar and see at a glance which ones they have already read
**Depends on**: Phase 03
**Requirements**: ARCH-01, ARCH-02, ARCH-03, ARCH-04, PROG-01, PROG-02
**Success Criteria** (what must be TRUE):
  1. User opens the archive page and sees a calendar grid showing all months that contain lesson content
  2. User can tap previous/next arrows to navigate between months without reloading the page
  3. User taps a day cell that has content and is taken to that day's lesson page
  4. Days without lesson content are visually distinct (greyed out) and cannot be tapped
  5. When a user opens a lesson page, that date is automatically saved to localStorage — no explicit action required
  6. Calendar day cells display a visual read indicator for dates recorded in localStorage
**Plans:** 2 plans
Plans:
- [ ] 02-01-PLAN.md — Scaffold Astro project with Tailwind 4, Content Collections, lesson list homepage, and stub lesson pages
- [ ] 02-02-PLAN.md — Add build-and-deploy CI/CD job to daily-content.yml and verify live GitHub Pages deployment
**UI hint**: yes

### Phase 05: Theme & Polish
**Goal**: Users experience a visually consistent site in dark or light mode that respects their system preference and remembers their manual override without any flash on page load
**Depends on**: Phase 02
**Requirements**: PROG-03, PROG-04, PROG-05, PROG-06
**Success Criteria** (what must be TRUE):
  1. On first visit, the site displays in dark mode if the user's OS is set to dark, and light mode if set to light — no configuration required
  2. User can tap a theme toggle on any page to switch between dark and light mode
  3. User's manual theme selection persists across browser sessions — returning to the site shows the previously chosen mode
  4. A user with dark mode active sees no flash of light background before the dark theme loads on any page
**Plans:** 2 plans
Plans:
- [ ] 02-01-PLAN.md — Scaffold Astro project with Tailwind 4, Content Collections, lesson list homepage, and stub lesson pages
- [ ] 02-02-PLAN.md — Add build-and-deploy CI/CD job to daily-content.yml and verify live GitHub Pages deployment
**UI hint**: yes

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Foundation | v1.0 | 2/2 | Complete | 2026-03-22 |
| 2. RSS Fetch | v1.0 | 1/2 | In Progress|  |
| 3. AI Pipeline | v1.0 | 3/3 | Complete | 2026-03-23 |
| 4. Provider Abstraction + OpenAI Integration | v1.1 | 2/2 | Complete | 2026-03-23 |
| 5. Fallback Logic | v1.1 | 1/1 | Complete | 2026-03-23 |
| 6. AI Provider Documentation | v1.1 | 2/2 | Complete | 2026-03-23 |
| 7. Custom Endpoint Implementation | v1.2 | 3/3 | Complete | 2026-03-23 |
| 8. Third-Party Provider Documentation | v1.2 | 1/1 | Complete | 2026-03-23 |
| 01. Gemini Migration | v1.3 | 2/2 | Complete | 2026-03-24 |
| 02. Astro Foundation | v2.0 | 2/2 | Complete    | 2026-03-24 |
| 03. Lesson Reading Experience | v2.0 | 0/? | Not started | - |
| 04. Archive Calendar | v2.0 | 0/? | Not started | - |
| 05. Theme & Polish | v2.0 | 0/? | Not started | - |
