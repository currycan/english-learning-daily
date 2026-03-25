# Website Milestone — Context

**Gathered:** 2026-03-24
**Status:** Pre-milestone — Ready for `/gsd:new-milestone` then phase planning

<domain>
## Scope

Build a static learning website that renders the daily Markdown lessons (`content/YYYY-MM-DD.md`) as a mobile-first reading experience accessible from any device. The website is a frontend-only consumer of existing content — it adds no AI generation, no new backend, no changes to the content pipeline.

Existing pipeline (GitHub Actions → Gemini → `content/YYYY-MM-DD.md` → git commit) continues unchanged. The website is an additional output built on top of that content.

</domain>

<decisions>
## Implementation Decisions

### Tech Stack
- **D-01:** Astro static site generator (not Vue/React/Next.js)
- **D-02:** GitHub Pages hosting, default domain (`username.github.io/study-all` or `/`)
- **D-03:** No backend, no database — pure static site

### Build & Deployment
- **D-04:** GitHub Actions: extend the existing `daily-content.yml` workflow to trigger an Astro build + GitHub Pages deploy after each new content commit
- **D-05:** Content index generated at build time — GitHub Actions outputs a JSON manifest (`src/content-index.json` or similar) listing all lessons with date and title metadata; Astro reads this at build time, NOT via GitHub API at runtime
- **D-06:** Single repository — website lives alongside the Python scripts, not a separate repo

### Site Structure
- **D-07:** Two views: Homepage (today's lesson) and Archive (calendar)
- **D-08:** Route structure: `/` (today), `/archive` (calendar), `/lesson/YYYY-MM-DD` (individual lesson)

### Homepage Layout
- **D-09:** Homepage shows today's lesson full-width at top
- **D-10:** Below the lesson, show a "Recent" list (last 5–7 days) as entry points
- **D-11:** Mobile-first single-column layout

### Lesson Content Display
- **D-12:** Four sections in the Markdown (`## 📖 文章`, `## 📚 词汇`, `## 🔗 表达`, `## ❓ 理解`) are parsed and displayed as separate blocks
- **D-13:** Article text (`📖`) is always visible, not collapsible — it's the primary content
- **D-14:** Vocabulary (`📚`), Chunking Expressions (`🔗`), and Comprehension (`❓`) sections are **collapsible** — collapsed by default, user taps to expand
- **D-15:** Comprehension Q&A: questions shown in expanded block; **answers hidden by default** with a "查看答案" tap-to-reveal per question (both EN + 中 answers revealed together)

### Archive View
- **D-16:** Calendar grid view (month-by-month), each day with content is a tappable cell
- **D-17:** Days with content shown as active; days without content shown as empty/grey
- **D-18:** Calendar cells marked as "read" use localStorage (see D-19)

### Reading Progress
- **D-19:** Browser localStorage tracks which lesson dates the user has read (`read_lessons: ["2026-03-24", ...]`)
- **D-20:** "Read" is triggered when the user opens a lesson page (not explicit marking)
- **D-21:** Calendar cells show a visual read/unread indicator (e.g., dot or fill color)

### Visual Design
- **D-22:** System dark/light mode via `prefers-color-scheme` — automatically follows OS setting
- **D-23:** Manual toggle to override system preference, persisted in localStorage
- **D-24:** Typography optimized for reading: comfortable line-height, appropriate font size for mobile

### Access Control
- **D-25:** Initially public — no access control in v2.0
- **D-26:** Access control is **explicitly deferred** — noted for a future phase if needed

</decisions>

<specifics>
## Content Format Reference

Current Markdown format (from `content/2026-03-24.md`):

```markdown
## 📖 文章 / Article
[Article text]
> Source: [URL]

## 📚 词汇 / Vocabulary
**word** (part of speech) （中文）— English definition.
> "Quote from article"

## 🔗 表达 / Chunking Expressions
**phrase** （中文）
English explanation.
- Example 1
- Example 2

## ❓ 理解 / Comprehension
**Q: [Question]**
**A (EN):** [English answer]
**A (中):** [Chinese answer]
```

The Astro Markdown parser must split on these `##` section headers. Each section type has a distinct rendering component.

Vocabulary: each entry is `**word** (POS) （中文）— definition` + quote — render as styled definition card.

Chunks: each entry is `**phrase** （中文）` + explanation + 2 examples — render similarly.

Q&A: `**Q:**` / `**A (EN):**` / `**A (中):**` — both answers revealed together on tap.

</specifics>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Content Pipeline
- `content/2026-03-24.md` — Representative sample of actual Markdown format; parser must handle this structure
- `.github/workflows/daily-content.yml` — Existing workflow to extend with Astro build step
- `plan/state.json` — State file (NOT needed by website; localStorage handles read progress independently)

### Project Rules
- `CLAUDE.md` — Project principles: immutability, no secrets in code, exit non-zero on failure
- `.planning/PROJECT.md` — Project context and constraints

</canonical_refs>

<code_context>
## Existing Code Insights

### Content Files
- All lessons in `content/YYYY-MM-DD.md` — Beijing timezone dates (UTC+8)
- Currently only one file exists (`2026-03-24.md`) — website must degrade gracefully when only one lesson exists

### GitHub Actions
- `daily-content.yml` — Main content generation workflow; Astro build should be added as a downstream job in this workflow after content commit succeeds
- `morning.yml` / `evening.yml` — Bark push workflows; unrelated to website

### Python Scripts
- No Python code is reused by the website; website is pure frontend

### Integration Points
- Build step reads `content/*.md` → generates JSON index → Astro consumes at build time
- Deploy step: `gh-pages` branch or GitHub Pages via Actions artifact

</code_context>

<deferred>
## Deferred Ideas

- **Access control / password protection** — explicitly punted to a future phase; v2.0 is public
- **Mark as done on website** (syncing with `plan/state.json`) — out of scope; website tracks "read" independently via localStorage
- **Search / filtering** — not in scope for v2.0
- **Audio pronunciation** — not in scope
- **User accounts / cross-device sync** — would require a backend; out of scope for static site

</deferred>

---

*Pre-milestone context — gathered 2026-03-24*
*Next step: `/gsd:new-milestone` to create v2.0 milestone with website phases*
