# Feature Research

**Domain:** Mobile-first static reading/learning website (Astro + GitHub Pages) — v2.0 website milestone
**Researched:** 2026-03-24
**Confidence:** HIGH — patterns are well-established across static site, reading app, and mobile UX domains; Astro-specific patterns verified via official docs and 2025 community examples.

> Note: This file supersedes the v1.x pipeline feature research. The content pipeline features (vocabulary, Q&A generation, etc.) are complete. This research covers only the website layer built on top of existing `content/YYYY-MM-DD.md` files.

---

## Feature Landscape

### Table Stakes (Users Expect These)

Features users assume exist in any reading/learning website. Missing these makes the product feel broken.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Today's lesson on homepage | Primary use case — user opens the site to read today's content; any other default is disorienting | LOW | D-09/D-10: full-width lesson at top, recent 5–7 day list below |
| Article text always visible | The article is the reason the user is here; requiring a tap to expand it before reading is a friction anti-pattern | LOW | D-13: `📖` section is never collapsible. Correct. |
| Collapsible secondary sections | Mobile screens are narrow; vocab/expressions/comprehension below the article would push it far off-screen | LOW | Use native `<details>/<summary>` — see UX Patterns section |
| Tap-to-reveal answers | Standard comprehension exercise pattern; showing answers immediately defeats active recall | LOW | Per-question reveal; no "reveal all" button — see UX Patterns section |
| Archive navigation | Users want to return to past lessons; without this the site is one-visit-only | MEDIUM | Calendar grid, days with content tappable, links to `/lesson/YYYY-MM-DD` |
| Comfortable mobile typography | A reading-focused site with uncomfortable font size or line spacing feels broken; this is the core UX | LOW | 16–18px body, 1.5–1.6 line-height, 44px min tap targets — see UX Specs section |
| Dark/light mode | Reading apps are used in low-light conditions; missing dark mode is painful and users notice immediately | MEDIUM | System auto-follow + manual toggle + no flash of wrong theme — see UX Patterns section |
| Graceful empty state | Content generates at noon Beijing time; morning visitors (primary use case) must not see a blank or broken page | LOW | Show most recent lesson with a label — see UX Patterns section |

### Differentiators (Competitive Advantage)

Features that distinguish this from a generic blog or static reading site.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Reading progress via localStorage | Calendar cells show which lessons the user has already read — creates a habit-tracking loop without any backend or login | LOW | Auto-mark on lesson page load (D-20); schema detailed below |
| Bilingual answer reveal | EN + Chinese answers revealed together in one tap — reduces cognitive switching for the target B1–B2 learner | LOW | Both `A (EN)` and `A (中)` sibling blocks revealed by a single `<details>` toggle |
| Visual read/unread indicators on calendar | Immediate feedback on study consistency — more motivating than a plain chronological list | LOW | CSS class toggled from localStorage read list at render time |
| Content-indexed calendar (not API-driven) | All lesson metadata resolved at build time; no runtime API calls, no loading spinners, instant interaction | LOW–MEDIUM | Build-time JSON manifest from `content/*.md` via Astro Content Collections |

### Anti-Features (Commonly Requested, Often Problematic)

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| "Expand all" / "Collapse all" button | Feels convenient for power users | Clutters small mobile screens; per-section toggles already cover the need; "reveal all answers" actively undermines learning | Per-section `<details>` elements handle this without extra UI chrome |
| Explicit "Mark as read" button | Some users want deliberate control | Adds tap friction; auto-marking on page open (D-20) is correct for 95% of use cases and matches the decision | Auto-mark via `DOMContentLoaded` — silent, no button needed |
| Quiz / scoring mode | Natural next step after Q&A reveal | Requires game-engine state, scoring UI, and session management — explicitly out of scope in PROJECT.md | Tap-to-reveal is the right stopping point for B1–B2 reading practice |
| Client-side full-text search | Useful as archive grows | Requires a search index library (Pagefind ≈ 20KB+) adding bundle weight; overkill for ≤90 lessons in year one | Calendar date navigation covers the primary retrieval use case |
| Cross-device sync for reading progress | Users read on phone and laptop | Requires a backend + user accounts — explicitly deferred in website-CONTEXT.md | Accept localStorage-only; document the limitation in UI copy |
| Pagination / "load more" on homepage | Seems needed as archive grows | Homepage recent list is intentionally 5–7 entries (D-10); all history is in the calendar | Keep homepage list shallow; calendar handles full history |
| Swipe-to-navigate between lessons | Feels native on mobile | Complex gesture handling; accessibility concerns; adds JS bundle; not needed for a reading app (pagination arrows suffice) | Previous/next arrow links on lesson pages |

---

## UX Patterns (Answers to Specific Research Questions)

### 1. Collapsible Sections: `<details>/<summary>` vs JS Accordion

**Recommendation: Native `<details>/<summary>`. No JavaScript needed.**

Rationale:
- Browser handles open/close state, keyboard navigation, and accessibility for free. No `aria-expanded` management required.
- Zero JavaScript overhead — faster first paint, no hydration, smaller bundle. Critical for mobile on slower connections.
- Universal browser support in 2025 (all major browsers including mobile Safari 6+, Chrome 120+, Firefox 130+). The `name` attribute for exclusive (mutually closing) accordions now works across all major engines.
- CSS can make `<details>` look identical to any custom accordion. Animated open/close transitions require a CSS workaround (the `grid` row-height trick or `interpolate-size: allow-keywords` in Chrome 129+) but are cosmetic, not functional.
- Accessibility caveat: revealed content is not always immediately announced by some screen reader/AT combinations. For this use case (sighted mobile learners) this is an acceptable tradeoff. If accessibility is a priority, add an `aria-live` region as an enhancement.

**Conclusion:** A JS accordion adds complexity with zero functional benefit for this scope. Use `<details>`.

### 2. Tap-to-Reveal Answers: Per-Question, No "Reveal All"

**Recommendation: One `<details>` toggle per question. No global reveal button.**

Rationale:
- The purpose of comprehension Q&A in language learning is active recall — the user should attempt an answer before seeing it. A "reveal all" button defeats this.
- Per-question granularity maps directly to the Markdown structure: each `**Q:**` / `**A (EN):**` / `**A (中):**` triplet is independent.
- Implementation: wrap each Q/A triplet in a `<details>` element. The `<summary>` contains the question text. The revealed content contains both answers. This is consistent with the vocabulary/expressions `<details>` pattern — one mental model for the entire page.
- Show question text in the summary, not a generic "Show answer" label. This lets users scan all questions before deciding which to attempt — matching the comprehension reading flow.
- Reveal both EN and Chinese answers together (D-15). Do not split them into two toggles.

**Button label:** "查看答案 ▼" (collapsed state) — bilingual convention consistent with the rest of the content.

### 3. Calendar Archive

**Data each calendar cell needs:**

| Field | Source | Notes |
|-------|--------|-------|
| `date` (YYYY-MM-DD) | Build-time content index | Used to construct `/lesson/YYYY-MM-DD` route and check for content |
| `hasContent` (boolean) | Build-time content index | Whether a `.md` file exists for this date |
| `title` (string or null) | Build-time content index | Optional; used for `title` attribute on cell link for screen readers |
| `isRead` (boolean) | Derived at runtime from localStorage | NOT stored in the build index; injected client-side after mount |

**Efficient rendering for 30–90 days:**
- Generate `content-index.json` at build time: array of `{ date, title }` objects. Astro reads `content/*.md` via `Astro.glob()` or Content Collections `glob()` loader.
- At 90 entries the JSON is approximately 5KB — no pagination or lazy-loading needed for v2.0.
- Calendar component receives the index as a prop; renders month-grid HTML entirely at build time (static HTML).
- `isRead` state injected via a small `<script is:inline>` after mount that reads localStorage and adds a CSS class to matching cells. No framework hydration required.
- Calendar must handle months with zero or one entry without layout breakage (current state: only one file, `2026-03-24.md`).

**Grid structure:** Standard ISO week layout (Mon–Sun), current month default, previous/next month navigation arrows. Days outside the current month: empty greyed cells.

### 4. Reading Progress via localStorage

**Recommended schema:**

```json
{
  "readLessons": ["2026-03-24", "2026-03-23"]
}
```

Store theme override in a separate key to keep concerns decoupled:

```json
{ "themeOverride": "dark" }
```

The date-array approach is simple and sufficient: O(n) lookup is acceptable for ≤365 entries/year (strings are short; 365 dates ≈ 4KB total).

**Edge cases and mitigations:**

| Edge Case | Behaviour | Mitigation |
|-----------|-----------|------------|
| Private/incognito mode | iOS Safari and Firefox in private mode may throw `SecurityError` on `localStorage.setItem`; Chrome/Edge: storage available but cleared on tab close | Wrap ALL localStorage access in `try/catch`. Degrade silently — progress just won't persist. Never surface an error to the user. |
| User clears browser storage | `readLessons` array disappears; calendar reverts to all-unread | Acceptable data loss — no recovery path without a backend. No special handling needed. |
| Multiple tabs | Two tabs opening the same lesson write the same date | Use set-semantics on write: `if (!list.includes(date)) list.push(date)` — idempotent |
| Storage quota exceeded | Extremely unlikely (≈4KB for a full year of dates) | `try/catch` on write handles this; no user-visible action needed |
| SSR / build-time render | Astro static build has no browser context | Access localStorage only inside `<script is:inline>` or `document.addEventListener('DOMContentLoaded', ...)` — never in `.astro` frontmatter |
| User reads from git (not website) | Those dates never written to localStorage | Acceptable; localStorage tracks website reads only, by design |

**Write timing:** Mark lesson as read immediately on lesson page load (D-20), not on scroll or explicit action. One `DOMContentLoaded` listener per lesson page writes the date if not already present.

### 5. Dark / Light Mode — No Flash of Wrong Theme

**Recommendation: CSS custom properties on `[data-theme]` attribute + inline synchronous script in `<head>`.**

The flash of wrong theme (FOWT) occurs because HTML is parsed and first-painted before any deferred JavaScript runs. The fix is a synchronous inline script in `<head>` that sets the theme attribute before first paint.

**Pattern:**

```html
<!-- In <head>, before any <link rel="stylesheet"> tags, with is:inline so Astro does not hoist or defer it -->
<script is:inline>
  (function() {
    var stored = null;
    try { stored = localStorage.getItem('themeOverride'); } catch(e) {}
    var prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    var theme = stored || (prefersDark ? 'dark' : 'light');
    document.documentElement.setAttribute('data-theme', theme);
  })();
</script>
```

**CSS structure:**

```css
:root {
  --color-bg: #ffffff;
  --color-text: #1a1a1a;
  --color-surface: #f5f5f5;
  --color-accent: #2563eb;
}
[data-theme="dark"] {
  --color-bg: #121212;
  --color-text: #e8e8e8;
  --color-surface: #1e1e1e;
  --color-accent: #60a5fa;
}
```

**Toggle button behaviour:** Set `localStorage.setItem('themeOverride', newTheme)` and `document.documentElement.setAttribute('data-theme', newTheme)` synchronously. No page reload. CSS custom properties cascade immediately.

**Why not the CSS `light-dark()` function:** Available in Chrome 123+, Firefox 120+, Safari 17.5+ but requires `color-scheme` property coordination and is less flexible for multi-token theming. The `data-theme` + custom properties pattern is more universally understood, easier to debug, and fully compatible with all modern browsers.

**Astro-specific note:** Mark the head script as `is:inline` to prevent Astro from hoisting it. If placed in a layout component, it runs on every page automatically.

### 6. Mobile Reading UX Specifications

Based on WCAG 2.5.5 (AAA) and current mobile typography guidance:

| Property | Recommended Value | Rationale |
|----------|-------------------|-----------|
| Body font size | 16–18px (1rem–1.125rem) | 16px is the mobile minimum; 18px preferred for sustained reading |
| Line height | 1.5–1.6 | Narrow mobile columns (40–60 chars) need more generous spacing than desktop |
| Max line length | 65–70ch | Prevents full-width layout from making lines unreadably long on landscape tablets |
| Min tap target | 44 × 44 CSS px | WCAG 2.5.5 AAA; applies to `<details>` summaries, reveal toggles, calendar cells, nav arrows |
| Tap target spacing | 8px minimum between adjacent targets | Reduces accidental taps in the calendar grid |
| Paragraph spacing | 1em bottom margin | Visual breathing room between article paragraphs |
| Section header size | 1.1rem–1.2rem | Sufficient hierarchy without excessive size contrast on small screens |
| `<details>` summary padding | min 12px vertical, 16px horizontal | Comfortable tap target for section toggles and answer reveals |

### 7. Empty State: No Content for Today

**Recommendation: Show the most recent available lesson with a clear date label and an explanatory note.**

Rationale:
- A blank page or "no content" message is ambiguous — users cannot tell if the site is broken or simply early.
- The most recent lesson is always genuinely useful content, not a degraded fallback.
- Morning is the primary reading time for this daily lesson format. Content generates at noon Beijing time (UTC+8). Most visits before noon will hit this state.

**Implementation:**
1. Build-time: content index knows the most recent lesson date.
2. Homepage component: if today's date (Asia/Shanghai) has no entry in the index, render the most recent lesson instead.
3. Display a subtle label: "今日课文将在中午更新 · Today's lesson updates at noon (BJT)" alongside the date of the shown lesson.
4. The "today" check must be client-side (user's local clock), since the static build runs at commit time in UTC. A small `<script>` can swap labels without re-rendering content.
5. If the archive is empty (no lessons yet), show a friendly onboarding message — this state should only occur before first content commit.

**Timezone edge case:** The Astro build runs on UTC GitHub Actions runners. The build is triggered by the content commit (D-04), so a successful daily content run always produces an up-to-date build before users are likely to visit. Stale builds (no new content that day) will show the previous lesson, which is acceptable.

---

## Feature Dependencies

```
Content Index (build-time JSON from content/*.md)
    required-by --> Homepage (today's lesson + recent list)
    required-by --> Archive Calendar (knows which dates have content)
    required-by --> Lesson Pages (getStaticPaths generates routes)

Lesson Pages (/lesson/YYYY-MM-DD)
    required-by --> Archive Calendar (cells must link somewhere)
    required-by --> Homepage recent list (links must resolve)

localStorage read tracking (written on lesson page load)
    required-by --> Calendar read/unread indicators (reads the list)
    requires     --> Lesson Pages (write happens during lesson page visit)

Dark/light mode (inline head script + CSS custom properties)
    required-by --> All pages (must be in shared layout)
    requires    --> CSS custom properties defined in base styles
```

### Dependency Notes

- **Content index before everything:** All pages consume the build-time index. It must be the first build-step implemented.
- **Lesson pages before calendar:** Calendar cells link to lesson pages; those routes must exist before calendar navigation is testable.
- **localStorage loop requires both ends:** Reading progress write happens on lesson pages; display happens on calendar. Both must be in place for the full feature to work. Can be partially tested by manually seeding localStorage.
- **Dark mode in shared layout:** The inline `<head>` script must be in the base layout to apply to all pages before first paint.

---

## MVP Definition

### Launch With (v2.0)

These are the requirements listed as Active in PROJECT.md. All are in scope for this milestone.

- [ ] Content index generated at build time from `content/*.md`
- [ ] Homepage: today's lesson full-width + recent 5–7 day list + empty state handling
- [ ] Lesson page: article visible, `<details>` for vocab/expressions/comprehension, per-question answer reveal
- [ ] Archive: calendar grid, days with content tappable, month navigation
- [ ] Reading progress: localStorage tracks read dates, calendar shows read/unread indicator
- [ ] Dark/light mode: system auto + manual toggle + localStorage persistence + no FOWT

### Add After Validation (v2.x)

- [ ] Section collapse state persisted in localStorage — add if users report re-expanding sections is annoying
- [ ] Previous/next lesson navigation links on lesson pages — convenient but not blocking; add if navigating via calendar proves cumbersome
- [ ] Streak counter on homepage — motivating; requires date arithmetic on read list

### Future Consideration (v3+)

- [ ] Client-side search (Pagefind) — only valuable once archive exceeds ~50 lessons
- [ ] Password protection — explicitly deferred in website-CONTEXT.md; add if site needs to be private

---

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Content index + lesson pages | HIGH | LOW | P1 |
| Article display (always visible) | HIGH | LOW | P1 |
| Collapsible sections via `<details>` | HIGH | LOW | P1 |
| Tap-to-reveal Q&A answers | HIGH | LOW | P1 |
| Dark/light mode with no FOWT | HIGH | LOW–MEDIUM | P1 |
| Mobile typography (font/line-height/tap targets) | HIGH | LOW | P1 |
| Homepage today + recent list | HIGH | LOW | P1 |
| Empty state (show most recent) | HIGH | LOW | P1 |
| Archive calendar view | MEDIUM | MEDIUM | P1 |
| localStorage reading progress | MEDIUM | LOW | P1 |
| Calendar read/unread indicators | MEDIUM | LOW | P1 |
| Previous/next lesson navigation | LOW | LOW | P2 |
| Section collapse persistence in localStorage | LOW | LOW | P3 |
| Streak counter | LOW | MEDIUM | P3 |

**Priority key:**
- P1: Must have for v2.0 launch
- P2: Should have when possible
- P3: Nice to have, future consideration

---

## Competitor Feature Analysis

| Feature | Duolingo (reference app) | Medium (reading reference) | Our Approach |
|---------|--------------------------|----------------------------|--------------|
| Collapsible study sections | Separate screens per exercise type | Not applicable | `<details>` in-page — no navigation cost |
| Tap-to-reveal | Card flip gesture | Not applicable | `<details>` summary expand — simpler, no gesture library |
| Reading progress | Per-lesson XP, streak counter | "X min read" estimate only | localStorage date array + calendar visual |
| Dark mode | System + manual toggle | System + manual toggle | System + manual + no FOWT via inline head script |
| Empty state | Never empty (procedural content) | Shows feed | Show most recent lesson + "updates at noon" label |
| Calendar archive | Lesson history grid | Archive page (chronological) | Month-grid calendar, active days highlighted, read/unread state |
| Typography | System font, comfortable spacing | Serif reading font, generous spacing | 16–18px body, 1.5–1.6 line-height, single column |

---

## Sources

- [MDN Blog: Exclusive accordions using HTML `<details>`](https://developer.mozilla.org/en-US/blog/html-details-exclusive-accordions/)
- [Hassell Inclusion: Accessible accordions with `<details>/<summary>`](https://www.hassellinclusion.com/blog/accessible-accordions-part-2-using-details-summary/)
- [Astro Content Collections — official docs](https://docs.astro.build/en/guides/content-collections/)
- [Building a Calendar Interface in Astro (2025)](https://myles.garden/2025/09/21/astro-calendar)
- [Fixing dark mode flash on server-rendered sites — Maxime Heckel](https://blog.maximeheckel.com/posts/switching-off-the-lights-part-2-fixing-dark-mode-flashing-on-servered-rendered-website/)
- [Best light/dark mode theme toggle — whitep4nth3r](https://whitep4nth3r.com/blog/best-light-dark-mode-theme-toggle-javascript/)
- [MDN: Window localStorage](https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage)
- [Font Size Guidelines for Responsive Websites — Learn UI Design](https://www.learnui.design/blog/mobile-desktop-website-font-size-guidelines.html)
- [Mobile typography accessibility — fontfyi](https://fontfyi.com/blog/mobile-typography-accessibility/)
- [Tap target size — Digital.gov / WCAG 2.5.5](https://digital.gov/guides/mobile-principles/tap-targets)
- [Empty state interface design — NN/g](https://www.nngroup.com/articles/empty-state-interface-design/)
- Project context: `.planning/website-CONTEXT.md` (D-01 through D-26)
- Project context: `.planning/PROJECT.md` (v2.0 Active requirements, Out of Scope constraints)
- Sample content: `content/2026-03-24.md` (actual Markdown format driving parser and display decisions)

---
*Feature research for: mobile-first static English learning website (Astro + GitHub Pages), v2.0 website milestone*
*Researched: 2026-03-24*
