# Requirements: v2.0 学习网站 (Learning Website)

## Active Requirements

### SITE — Site Infrastructure & CI/CD

- [ ] **SITE-01**: User can access the learning website at the GitHub Pages default URL
- [ ] **SITE-02**: Website automatically rebuilds and deploys when a new `content/*.md` file is committed
- [ ] **SITE-03**: Website builds from `content/*.md` files at build time — no runtime API calls
- [ ] **SITE-04**: Astro project lives in a `website/` subdirectory, isolated from Python scripts

### LESS — Lesson Reading Experience

- [ ] **LESS-01**: User can view today's lesson on the homepage (most recent available if today's not yet committed)
- [ ] **LESS-02**: Homepage shows a list of recent lessons (last 5–7 days) below today's lesson
- [ ] **LESS-03**: Homepage shows a "今日课文将在中午更新" label when today's content has not yet been committed
- [ ] **LESS-04**: User can read the full article text on any lesson page
- [ ] **LESS-05**: User can expand/collapse the vocabulary (📚) section on a lesson page
- [ ] **LESS-06**: User can expand/collapse the chunking expressions (🔗) section on a lesson page
- [ ] **LESS-07**: User can expand/collapse the comprehension questions (❓) section on a lesson page
- [ ] **LESS-08**: User can reveal the answer to each comprehension question individually (EN + ZH shown together)
- [ ] **LESS-09**: Lesson pages are readable on mobile (≥16px body text, ≥44px tap targets)

### ARCH — Archive Calendar

- [ ] **ARCH-01**: User can view a calendar showing all months that have lesson content
- [ ] **ARCH-02**: User can navigate between months in the calendar
- [ ] **ARCH-03**: User can tap a calendar day cell to open that day's lesson
- [ ] **ARCH-04**: Calendar cells for days without content are visually distinct (greyed out, not tappable)

### PROG — Reading Progress & Theme

- [ ] **PROG-01**: User's read lessons are automatically recorded in browser localStorage when a lesson page is opened
- [ ] **PROG-02**: Calendar day cells show a visual read/unread indicator based on localStorage
- [ ] **PROG-03**: Site follows the system dark/light mode preference automatically on first visit
- [ ] **PROG-04**: User can manually toggle between dark and light mode
- [ ] **PROG-05**: User's manual theme preference persists across browser sessions (localStorage)
- [ ] **PROG-06**: Dark mode activates without a visible flash of wrong theme (FOUC) on page load

## Future Requirements

- Access control / link-based privacy — deferred to v2.1 if needed
- Cross-device reading progress sync — requires backend; out of scope for static site

## Out of Scope

| Feature | Reason |
|---------|--------|
| User accounts / login | Static site; no backend |
| Cross-device reading progress sync | Would require a backend/API |
| Audio pronunciation | Text-only per project constraints |
| Search / filtering lessons | Not in v2.0 scope |
| Lesson rating or feedback | No backend |
| Custom domain | Using GitHub Pages default domain; upgrade deferred |
| Quiz / gamification | Tap-to-reveal Q&A covers the learning need |

## Traceability

*Filled by roadmapper.*

| REQ-ID | Phase | Notes |
|--------|-------|-------|
| — | — | — |
