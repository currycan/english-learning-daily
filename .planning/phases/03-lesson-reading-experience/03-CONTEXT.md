# Phase 03: Lesson Reading Experience - Context

**Gathered:** 2026-03-24
**Status:** Ready for planning

<domain>
## Phase Boundary

Transform the Phase 02 stub Astro site into a full lesson reading experience:
- Homepage: today's lesson full inline + recent lessons list
- Lesson pages (`/lesson/YYYY-MM-DD`): collapsible vocabulary/expressions/comprehension sections with tap-to-reveal answers

This phase does NOT deliver the archive calendar (Phase 04) or theme/dark-mode polish (Phase 05). All content comes from existing `content/*.md` files — no changes to the content pipeline.

</domain>

<decisions>
## Implementation Decisions

### Homepage Layout
- **D-01:** Homepage displays today's lesson **full inline** — article text (always visible) + collapsible vocabulary/expressions/comprehension sections. Users can learn without navigating away.
- **D-02:** Each lesson (homepage and lesson pages) includes an **原文跳转链接** (link to original source URL). The source URL is already embedded in the Markdown as `> Source: https://...`.
- **D-03:** When today's lesson has not yet been committed, the homepage shows the **most recently available lesson** (typically yesterday's) as the main content, with a **notice bar at the top**: "⚠️ 今日课文将在中午更新". The main lesson area is never empty.

### Recent Lessons List
- **D-04:** Show the **5 most recent lessons** below today's lesson (LESS-02 range was 5–7; user chose 5).
- **D-05:** Each list item shows: **date + first sentence of article text** as a preview (e.g., "2026-03-23 · Paris has a big problem with trash, and it is..."). Article headline is extracted from the first non-empty line of the `## 📖 文章` section.

### Collapsible Sections
- **D-06:** Vocabulary (📚), Chunking Expressions (🔗), and Comprehension (❓) sections are **collapsed by default**.
- **D-07:** Collapse/expand is **JS-driven with smooth animation** (not native `<details>`). Implement via `is:inline` script or Astro island — smooth open/close transition.
- **D-08:** Article text (📖) is **always visible**, never collapsible — it's the primary reading content.

### Comprehension Q&A
- **D-09:** Questions are shown when the ❓ section is expanded. Each question's answer is **hidden by default** with a tap-to-reveal button. Both EN and ZH answers are revealed together on tap (LESS-08).

### Markdown Parsing
- **D-10:** The four Markdown sections (`## 📖 文章`, `## 📚 词汇`, `## 🔗 表达`, `## ❓ 理解`) must be parsed into separate renderable blocks. Parsing strategy is Claude's discretion — options include string splitting on `## ` headers at build time in the Astro page, or a remark plugin. String splitting in the Astro frontmatter is simpler and sufficient.

### Mobile Reading
- **D-11:** Mobile-first (LESS-09): ≥16px body text, ≥44px tap targets for all interactive elements (section headers, answer reveal buttons). Already enforced by `max-w-[640px]` container in Base.astro.

### Claude's Discretion
- Exact animation duration/easing for collapse transitions
- Whether to extract source URL via regex or markdown parsing
- Internal component structure (single page component vs separate Astro components per section type)
- How to render vocabulary entries (styled definition card — per website-CONTEXT.md D-12 specifics)
- Exact styling for the notice bar ("⚠️ 今日课文将在中午更新")

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Content Format
- `content/2026-03-24.md` — Representative sample of actual Markdown format. Parser must handle: `## 📖 文章 / Article`, `## 📚 词汇 / Vocabulary`, `## 🔗 表达 / Chunking Expressions`, `## ❓ 理解 / Comprehension` section headers. Vocabulary entries use `**word** (POS) （中文）— definition` + `> quote` format. Q&A uses `**Q:**` / `**A (EN):**` / `**A (中):**` format.

### Prior Context
- `.planning/website-CONTEXT.md` — Full pre-milestone decisions (D-12 through D-24). D-12: sections parsed separately. D-13: article always visible. D-14: vocab/chunks/Q&A collapsible. D-15: tap-to-reveal Q&A answers. D-24: typography for reading (comfortable line-height, appropriate font size).
- `.planning/phases/02-astro-foundation/02-CONTEXT.md` — Phase 02 decisions. D-03: homepage stub to be replaced. D-04: lesson pages are stubs at `/lesson/YYYY-MM-DD`. D-06: Astro 6, `base: '/study-all'`. D-07: Tailwind CSS 4 via `@tailwindcss/vite`.

### Existing Code (Phase 02 foundation)
- `website/src/pages/index.astro` — Stub homepage (lesson list); Phase 03 replaces this with full reading layout
- `website/src/pages/lesson/[id].astro` — Stub lesson page (`<Content />`); Phase 03 replaces with section-parsed reading UI
- `website/src/layouts/Base.astro` — Base layout (`max-w-[640px] mx-auto px-4 py-8`); reuse as-is
- `website/src/content.config.ts` — Content Collections with `glob()` loader; no changes needed

### Requirements
- `.planning/REQUIREMENTS.md` — LESS-01 through LESS-09 define acceptance criteria for this phase

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `Base.astro` layout — already handles container width, padding; Phase 03 adds content inside the slot
- `getCollection('lessons')` + `getStaticPaths()` patterns — already established in both page files; reuse as-is
- `render(entry)` from `astro:content` — already working in `[id].astro`; useful for rendering the article section if needed, or can bypass with raw string parsing

### Established Patterns
- Tailwind CSS 4 (`@import "tailwindcss"` in `global.css`) — no config file, utility classes available
- Lesson IDs are ISO date strings (`YYYY-MM-DD`) — use for date comparison and sorting
- All lessons sorted descending by `lesson.id.localeCompare()` — reuse this pattern

### Integration Points
- `index.astro`: replace the `<ul>` lesson list with homepage layout (today's lesson inline + recent list)
- `lesson/[id].astro`: replace `<article class="prose"><Content /></article>` with section-parsed reading UI
- No new routes needed; no changes to `content.config.ts` or `Base.astro`
- No new npm packages strictly required (JS animation can be vanilla; if `@tailwindcss/typography` is desired for prose styling, that's Claude's discretion)

</code_context>

<specifics>
## Specific Ideas

- Notice bar mockup confirmed: `⚠️ 今日课文将在中午更新` as a top-of-page banner, with yesterday's (most recent available) lesson shown as main content below.
- Recent list item format confirmed: `2026-03-23 · Paris has a big problem with trash, and it is...` — date + first sentence truncated.
- Collapse animation: smooth open/close (not instant toggle). Duration and easing at Claude's discretion.
- Source URL: extract from `> Source: URL` line in the 📖 section; render as a visible "阅读原文 →" link.

</specifics>

<deferred>
## Deferred Ideas

- **《新概念英语 2-3》内容集成** — User raised the idea of integrating New Concept English books 2-3 as an additional content source. This is a new capability (content source expansion) and belongs in a future phase. Worth considering when planning Phase 06+ or a new milestone.
- **Archive calendar** (Phase 04) — calendar grid with read/unread indicators; builds on localStorage write added in this phase (PROG-01 tracking starts here, consumed by Phase 04).
- **Dark/light mode toggle** (Phase 05) — theme system deferred to Phase 05; Phase 03 inherits system default.

</deferred>

---

*Phase: 03-lesson-reading-experience*
*Context gathered: 2026-03-24*
