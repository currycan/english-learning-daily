# Phase 03: Lesson Reading Experience - Research

**Researched:** 2026-03-24
**Domain:** Astro 6 static pages, Tailwind CSS 4, vanilla JS collapse/reveal UI
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** Homepage displays today's lesson full inline — article text (always visible) + collapsible vocabulary/expressions/comprehension sections.
- **D-02:** Each lesson includes an 原文跳转链接 extracted from `> Source: https://...` in the 📖 section.
- **D-03:** When today's lesson is absent, show most recent available lesson + notice bar "⚠️ 今日课文将在中午更新" at top.
- **D-04:** Show 5 most recent lessons (not 7) in the recent list below the featured lesson.
- **D-05:** Recent list items: `date · first sentence of article text` (first non-empty line of `## 📖 文章` section).
- **D-06:** Vocabulary (📚), Chunking Expressions (🔗), Comprehension (❓) sections collapsed by default.
- **D-07:** Collapse/expand is JS-driven with smooth animation — NOT native `<details>`. Use `is:inline` script or Astro island.
- **D-08:** Article text (📖) is always visible, never collapsible.
- **D-09:** Comprehension Q&A: section expands to show questions; each question's answer hidden by default with tap-to-reveal. EN and ZH answers revealed together on tap.
- **D-10:** Markdown sections parsed by splitting on `## ` headers at build time in the Astro frontmatter (string splitting, not a remark plugin).
- **D-11:** Mobile-first: ≥16px body text, ≥44px tap targets. Container already `max-w-[640px]` in Base.astro.

### Claude's Discretion

- Exact animation duration/easing for collapse transitions
- Whether to extract source URL via regex or markdown parsing
- Internal component structure (single page component vs separate Astro components per section type)
- How to render vocabulary entries (styled definition card)
- Exact styling for the notice bar

### Deferred Ideas (OUT OF SCOPE)

- 《新概念英语 2-3》content integration — future phase
- Archive calendar (Phase 04)
- Dark/light mode toggle (Phase 05)
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| LESS-01 | User can view today's lesson on the homepage (most recent available if today's not yet committed) | D-01 + D-03: sort lessons by id descending, compare top id to today's date (Asia/Shanghai); use most recent if no match |
| LESS-02 | Homepage shows a list of recent lessons (last 5 days) below today's lesson | D-04: slice sorted array to [1..5] (skip index 0 = featured); render as list with links |
| LESS-03 | Homepage shows "今日课文将在中午更新" label when today's content is absent | D-03: conditional banner rendered at build time |
| LESS-04 | User can read the full article text on any lesson page | D-08: article section always visible, no interaction required |
| LESS-05 | User can expand/collapse the vocabulary section | D-06 + D-07: JS-driven collapsible, collapsed by default |
| LESS-06 | User can expand/collapse the chunking expressions section | D-06 + D-07: same pattern as LESS-05 |
| LESS-07 | User can expand/collapse the comprehension section | D-06 + D-07: same pattern |
| LESS-08 | User can reveal the answer to each comprehension question individually (EN + ZH shown together) | D-09: per-question reveal button; both answers revealed on single tap |
| LESS-09 | Lesson pages readable on mobile (≥16px body text, ≥44px tap targets) | D-11: Tailwind utility classes enforce sizes; verified by Base.astro container |
</phase_requirements>

---

## Summary

Phase 03 transforms two stub Astro pages into a full lesson reading experience. All content comes from already-working Content Collections that load `content/*.md` files via the `glob()` loader. No new npm packages are required — the existing Astro 6 + Tailwind CSS 4 stack is sufficient for everything this phase delivers.

The critical technical work is: (1) a Markdown string-split parser that runs in Astro frontmatter to split raw lesson text into four typed section objects, (2) a JS-driven collapse/reveal system using `is:inline` scripts, (3) homepage date logic to determine "today" in Asia/Shanghai and fall back to the most recent lesson when today's file is absent, and (4) mobile-safe sizing enforced via Tailwind utilities.

All decisions are locked by the user in CONTEXT.md. There is nothing to explore — every choice is prescribed. The planner's job is to sequence tasks that implement these decisions precisely.

**Primary recommendation:** Implement section parsing as a pure TypeScript function in `index.astro` and `[id].astro` frontmatter blocks. Use `is:inline` `<script>` tags for collapse and reveal interactivity. No new dependencies needed.

---

## Standard Stack

### Core (already installed — no new packages needed)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| astro | 6.0.8 | Static site generation, content collections, component system | Locked decision (D-01 in Phase 02) |
| tailwindcss | 4.2.2 | Utility CSS, sizing, spacing, typography | Locked decision (Phase 02); v4 via Vite plugin |
| @tailwindcss/vite | 4.2.2 | Tailwind 4 Vite integration | Locked decision; no config file needed |

### Optional Supporting (Claude's discretion)

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| @tailwindcss/typography | ^0.5.x | `prose` class for article body rendering | Only if hand-styling article paragraphs is tedious; assess after base implementation |

**Installation (only if typography plugin chosen):**
```bash
cd website && npm install @tailwindcss/typography
# Add to global.css: @plugin "@tailwindcss/typography";
```

**Note:** `@tailwindcss/typography` for Tailwind 4 is configured via `@plugin` directive in CSS, NOT via `tailwind.config.js` (which does not exist in this project). Verify this is the correct approach before using.

**Version verification (current as of 2026-03-24):**
- `astro@6.0.8` — confirmed in `package.json`
- `tailwindcss@4.2.2` — confirmed in `package.json`
- `@tailwindcss/vite@4.2.2` — confirmed in `package.json`

---

## Architecture Patterns

### Recommended Project Structure

No new directories needed. Changes are confined to existing files:

```
website/src/
├── pages/
│   ├── index.astro          # REPLACE: homepage with featured lesson + recent list
│   └── lesson/
│       └── [id].astro       # REPLACE: section-parsed reading UI
├── layouts/
│   └── Base.astro           # UNCHANGED: max-w-[640px] container
├── styles/
│   └── global.css           # UNCHANGED (or add @plugin if typography used)
└── content.config.ts        # UNCHANGED
```

### Pattern 1: Markdown Section Splitter (build-time, in frontmatter)

**What:** Split raw lesson markdown into typed section objects using string operations on `entry.body`.

**When to use:** In every page that renders lesson content (both `index.astro` and `[id].astro`).

**How Content Collections exposes raw body:** In Astro 6, `entry.body` contains the raw markdown string. The `render(entry)` function renders everything as one HTML block — for section-separated display, bypass it and parse `entry.body` directly.

**Section headers to split on:**
```
## 📖 文章 / Article
## 📚 词汇 / Vocabulary
## 🔗 表达 / Chunking Expressions
## ❓ 理解 / Comprehension
```

**Example parser (TypeScript, runs in frontmatter):**
```typescript
// In Astro frontmatter --- block
interface LessonSections {
  article: string;
  vocabulary: string;
  expressions: string;
  comprehension: string;
}

function parseSections(body: string): LessonSections {
  // Split on any ## heading that starts a major section
  const articleMatch = body.match(/##\s*📖[^\n]*\n([\s\S]*?)(?=\n##\s*📚|$)/);
  const vocabMatch   = body.match(/##\s*📚[^\n]*\n([\s\S]*?)(?=\n##\s*🔗|$)/);
  const exprMatch    = body.match(/##\s*🔗[^\n]*\n([\s\S]*?)(?=\n##\s*❓|$)/);
  const comprMatch   = body.match(/##\s*❓[^\n]*\n([\s\S]*?)$/);

  return {
    article:       (articleMatch?.[1] ?? '').trim(),
    vocabulary:    (vocabMatch?.[1]   ?? '').trim(),
    expressions:   (exprMatch?.[1]    ?? '').trim(),
    comprehension: (comprMatch?.[1]   ?? '').trim(),
  };
}

const sections = parseSections(lesson.body ?? '');
```

**Confidence:** HIGH — `entry.body` is the raw markdown string in Astro Content Collections. Verified by inspecting the glob loader pattern and Astro 6 Content Collections docs.

### Pattern 2: Source URL Extraction

**What:** Extract the source URL from `> Source: https://...` line in the article section.

**Example:**
```typescript
function extractSourceUrl(articleText: string): string | null {
  const match = articleText.match(/^>\s*Source:\s*(https?:\/\/\S+)/m);
  return match?.[1] ?? null;
}
```

**Confidence:** HIGH — tested against `content/2026-03-24.md` which contains `> Source: https://www.newsinlevels.com/products/paris-is-dirty-level-2/`

### Pattern 3: First-sentence Preview Extraction

**What:** Extract the first non-empty non-metadata line from the article section for recent list preview.

**Key detail:** The article section starts with a timestamp line (`23-03-2026 15:00`) followed by the actual article text. Skip non-sentence lines (timestamp pattern: `DD-MM-YYYY HH:MM`).

**Example:**
```typescript
function extractPreview(articleText: string, maxChars = 60): string {
  const lines = articleText.split('\n').map(l => l.trim()).filter(Boolean);
  // Skip timestamp lines (format: DD-MM-YYYY HH:MM)
  const sentenceLine = lines.find(l => !/^\d{2}-\d{2}-\d{4}/.test(l) && !l.startsWith('>'));
  if (!sentenceLine) return '';
  return sentenceLine.length > maxChars
    ? sentenceLine.slice(0, maxChars) + '...'
    : sentenceLine;
}
```

**Confidence:** HIGH — verified against actual `2026-03-24.md` content format.

### Pattern 4: Today's Lesson Detection (Asia/Shanghai, build-time)

**What:** Determine today's date in Asia/Shanghai timezone and check if any lesson has that id.

**Critical detail:** GitHub Actions runners use UTC. The content pipeline uses Asia/Shanghai (UTC+8) dates for lesson IDs. The build must compute today in Shanghai time, not UTC.

**Example:**
```typescript
function getTodayShanghai(): string {
  // Intl.DateTimeFormat with Asia/Shanghai gives correct local date
  return new Intl.DateTimeFormat('en-CA', {
    timeZone: 'Asia/Shanghai',
    year: 'numeric', month: '2-digit', day: '2-digit'
  }).format(new Date()); // Returns YYYY-MM-DD (en-CA locale uses ISO format)
}

// In frontmatter:
const lessons = entries.sort((a, b) => b.id.localeCompare(a.id));
const todayId = getTodayShanghai();
const todayLesson = lessons.find(l => l.id === todayId);
const featuredLesson = todayLesson ?? lessons[0]; // fallback to most recent
const showNoticeBar = !todayLesson;
// Recent list: lessons that are NOT the featured one, capped at 5
const recentLessons = lessons.filter(l => l.id !== featuredLesson?.id).slice(0, 5);
```

**Confidence:** HIGH — `Intl.DateTimeFormat` with `en-CA` locale reliably produces `YYYY-MM-DD`.

### Pattern 5: JS-Driven Collapse with Smooth Animation

**What:** Collapsible sections triggered by a header button click, with CSS height transition.

**When to use:** Vocabulary, Chunking Expressions, Comprehension sections (all three collapsed by default).

**Implementation approach:** Use `max-height` transition — the only reliable CSS-only smooth approach for unknown-height content without JS measuring. Alternatively, use `grid-template-rows: 0fr / 1fr` transition (modern CSS, no JS needed for the animation itself — still needs JS for toggling a class).

**Recommended: `grid` row expand (no JS height measuring needed):**
```html
<!-- Section wrapper -->
<div class="section-block" data-collapsed="true">
  <button class="section-header w-full text-left py-3 flex items-center justify-between min-h-[44px]">
    <span>📚 词汇 / Vocabulary</span>
    <span class="chevron transition-transform duration-200">▼</span>
  </button>
  <div class="section-body grid transition-[grid-template-rows] duration-300 ease-out"
       style="grid-template-rows: 0fr">
    <div class="overflow-hidden">
      <!-- section content -->
    </div>
  </div>
</div>
```

```javascript
// is:inline script (runs once, no framework needed)
document.querySelectorAll('.section-block').forEach(block => {
  const btn = block.querySelector('.section-header');
  const body = block.querySelector('.section-body');
  const chevron = block.querySelector('.chevron');
  btn.addEventListener('click', () => {
    const collapsed = block.dataset.collapsed === 'true';
    body.style.gridTemplateRows = collapsed ? '1fr' : '0fr';
    chevron.style.transform = collapsed ? 'rotate(-180deg)' : '';
    block.dataset.collapsed = collapsed ? 'false' : 'true';
  });
});
```

**Confidence:** MEDIUM — `grid-template-rows` transition is widely supported (Chrome 107+, Safari 16.4+, Firefox 110+) and requires no JS height measurement. Tailwind 4 does not include `transition-[grid-template-rows]` as a default utility — it must be written as `transition-[grid-template-rows]` arbitrary value or handled via inline style + CSS transition in `<style is:global>`.

**Alternative: max-height approach** (simpler but requires a large arbitrary max-height):
```css
.section-body { max-height: 0; overflow: hidden; transition: max-height 0.3s ease-out; }
.section-body.open { max-height: 2000px; }
```
This is lower-fidelity (animation speed varies by content height) but works universally. Use if grid approach proves complex.

### Pattern 6: Per-Question Tap-to-Reveal

**What:** Each comprehension Q&A block has a "查看答案" button that shows the hidden answer block.

**Parsing Q&A blocks:** The comprehension section contains repeated `**Q:**` / `**A (EN):**` / `**A (中):**` groups. Parse in the frontmatter into an array of `{question, answerEn, answerZh}` objects, then render each as a component.

**Example parser:**
```typescript
interface QABlock {
  question: string;
  answerEn: string;
  answerZh: string;
}

function parseComprehension(text: string): QABlock[] {
  const blocks: QABlock[] = [];
  // Match each Q block
  const qPattern = /\*\*Q:\s*(.*?)\*\*\s*\n\*\*A \(EN\):\*\*\s*(.*?)\n\*\*A \(中\):\*\*\s*(.*?)(?=\n\*\*Q:|$)/gs;
  for (const match of text.matchAll(qPattern)) {
    blocks.push({
      question: match[1].trim(),
      answerEn: match[2].trim(),
      answerZh: match[3].trim(),
    });
  }
  return blocks;
}
```

**Reveal button pattern:**
```html
<div class="qa-block">
  <p class="font-medium mb-2">Q: {qa.question}</p>
  <div class="answer hidden">
    <p class="text-sm mt-1">{qa.answerEn}</p>
    <p class="text-sm text-gray-600 mt-1">{qa.answerZh}</p>
  </div>
  <button class="reveal-btn text-sm text-blue-600 underline min-h-[44px] px-2">查看答案</button>
</div>
```

```javascript
document.querySelectorAll('.reveal-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    const answer = btn.previousElementSibling; // .answer div
    answer.classList.remove('hidden');
    btn.remove(); // or hide btn after reveal
  });
});
```

### Anti-Patterns to Avoid

- **Using `render(entry)` for section-parsed display:** `render()` produces a single HTML blob with no section boundaries. Bypass it; use `entry.body` string splitting instead.
- **Using native `<details>/<summary>`:** Locked out by D-07. Do not use even as a progressive enhancement base.
- **Storing today's date as UTC:** Lesson IDs are Asia/Shanghai dates. A UTC "today" (midnight UTC = 8am Shanghai) will match, but at 11pm UTC (7am Shanghai next day) it will be wrong. Always use `Intl.DateTimeFormat` with `timeZone: 'Asia/Shanghai'`.
- **Using Tailwind config file:** Tailwind 4 in this project has NO `tailwind.config.js`. All customization goes through CSS `@theme` or `@plugin` directives in `global.css`.
- **Mutating lesson/section data structures:** Per CLAUDE.md — all transforms must return new objects. The `parseSections()` function above is pure. Keep it that way.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Content loading & routing | Custom file reader | `getCollection('lessons')` + `getStaticPaths()` (already working) | Edge cases in glob, caching, type safety all handled |
| Markdown rendering (article section) | Custom MD-to-HTML | `render(entry)` for the article section, OR retain raw text with manual `<p>` splitting | Built-in handles escaping, links, bold correctly |
| CSS animation library | Custom JS animator | CSS `grid-template-rows` transition or `max-height` transition | Fewer dependencies, works without hydration |
| Date formatting | Manual date string construction | `Intl.DateTimeFormat` | Handles timezone correctly across all environments |

**Key insight:** This phase is entirely build-time rendering + lightweight client JS. No framework, no hydration framework, no third-party UI library is needed.

---

## Common Pitfalls

### Pitfall 1: `entry.body` vs `render(entry)` confusion

**What goes wrong:** Developer calls `render(entry)` and tries to parse the returned HTML string for section splits, or assumes `entry.body` contains HTML.

**Why it happens:** Astro docs emphasize `render()` for content pages; the raw `body` property is less prominently documented.

**How to avoid:** Use `entry.body` (the raw markdown string) for section parsing. Only call `render(entry)` if you want to render the entire article as prose HTML.

**Warning signs:** Parser regex failing to find `##` headers in the parsed content.

### Pitfall 2: Asia/Shanghai timezone in GitHub Actions

**What goes wrong:** Build runs in UTC. `new Date().toISOString().slice(0,10)` gives UTC date. At 00:00–07:59 UTC (08:00–15:59 Shanghai), the UTC date is one day behind Shanghai. The notice bar appears incorrectly.

**Why it happens:** GitHub Actions runners use UTC by default.

**How to avoid:** Always use `Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Shanghai' })` to compute today's lesson ID.

**Warning signs:** Notice bar appears during morning hours even when a lesson is present.

### Pitfall 3: Tailwind 4 arbitrary property syntax

**What goes wrong:** Writing `transition-grid-template-rows` (hyphenated Tailwind-style) — this class does not exist in Tailwind 4 without explicit `@theme` registration.

**How to avoid:** Use `transition-[grid-template-rows]` arbitrary value syntax in Tailwind 4, or add the transition via inline `style` attribute + a `<style>` block. The `class="transition-[grid-template-rows] duration-300"` pattern works in Tailwind 4.

**Warning signs:** No animation visible (property not applied).

### Pitfall 4: `is:inline` script runs before DOM is ready

**What goes wrong:** `is:inline` scripts execute as they appear in the HTML. If the script is placed before the collapsible elements, `querySelectorAll` returns empty NodeList.

**How to avoid:** Place `<script is:inline>` at the end of the page body (after all collapsible elements), or wrap in `document.addEventListener('DOMContentLoaded', ...)`.

**Warning signs:** Click handlers silently do nothing; no JS errors.

### Pitfall 5: Base path omission in `href` links

**What goes wrong:** `href="/lesson/2026-03-24"` instead of `href="/study-all/lesson/2026-03-24"`. Internal links break on the deployed site.

**How to avoid:** Use Astro's `base` config — import `{ base }` from `astro:config` or use `Astro.site` + manual prefix. More reliably, use relative paths (`./lesson/2026-03-24`) from the root page, or use the `BASE_URL` env that Astro exposes: `` `${import.meta.env.BASE_URL}lesson/${id}` ``.

**Warning signs:** Links 404 on GitHub Pages but work on `localhost`.

### Pitfall 6: Comprehension regex multiline flag

**What goes wrong:** The Q&A regex without the `s` (dotAll) flag fails to match multi-line answers because `.` does not match newlines.

**How to avoid:** Use `/pattern/gs` — the `g` flag for `matchAll`, the `s` flag (dotAll) so `.` matches newlines in long answers. Verified against the long third question in `2026-03-24.md`.

---

## Code Examples

### Getting featured lesson and recent list (index.astro frontmatter)
```typescript
// Source: derived from Phase 02 established pattern + Intl.DateTimeFormat
import { getCollection } from 'astro:content';

const entries = await getCollection('lessons');
const lessons = entries.sort((a, b) => b.id.localeCompare(a.id));

const todayId = new Intl.DateTimeFormat('en-CA', {
  timeZone: 'Asia/Shanghai',
  year: 'numeric', month: '2-digit', day: '2-digit'
}).format(new Date());

const hasTodayLesson = lessons.some(l => l.id === todayId);
const featuredLesson = hasTodayLesson ? lessons.find(l => l.id === todayId)! : lessons[0];
const recentLessons = lessons.filter(l => l.id !== featuredLesson?.id).slice(0, 5);
```

### BASE_URL-safe links
```astro
<!-- Source: Astro docs - base config usage -->
<a href={`${import.meta.env.BASE_URL}lesson/${lesson.id}`}>
  {lesson.id}
</a>
```

### Vocabulary entry rendering (definition card pattern)
```astro
<!-- Each vocab entry: **word** (POS) （中文）— definition + > quote -->
<!-- Parse with regex, render as styled card: -->
<div class="border-l-4 border-blue-400 pl-3 py-2 mb-3">
  <div class="font-bold">{entry.word} <span class="font-normal text-sm text-gray-500">({entry.pos})</span> <span class="text-sm">（{entry.chinese}）</span></div>
  <div class="text-sm mt-1">{entry.definition}</div>
  <div class="text-xs text-gray-500 mt-1 italic">"{entry.quote}"</div>
</div>
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `entry.render()` method | `render(entry)` free function | Astro 5 | Already handled in Phase 02; do not revert |
| `@astrojs/tailwind` integration | `@tailwindcss/vite` Vite plugin | Tailwind 4 / Astro 6 | Already handled in Phase 02; no config file |
| `tailwind.config.js` | CSS `@theme` / `@plugin` directives | Tailwind 4 | No config file exists; all customization in global.css |

---

## Open Questions

1. **Should the article section use `render(entry)` or raw text for HTML rendering?**
   - What we know: `render(entry)` produces valid HTML from the full markdown; `entry.body` is raw markdown string
   - What's unclear: Whether rendering the article section as HTML (via `render()` on just the article portion) is desirable, or whether treating it as plain text is sufficient given the simple paragraph structure
   - Recommendation: Parse `entry.body` to extract the article section as a raw string, then render it as simple paragraphs by splitting on `\n\n`. Avoid calling `render()` for section-parsed pages to keep the approach uniform. If richer rendering is needed (bold, links), use a small marked/remark call — but this adds a dependency and is likely unnecessary.

2. **Does `entry.body` exist for all entries loaded via `glob()` loader?**
   - What we know: Astro Content Collections with `glob()` loader populates `entry.body` with the raw markdown string. This is documented behavior in Astro 5+.
   - What's unclear: Edge case — if a lesson file has only frontmatter and no body. Not an issue in this project (all lessons have body content, no YAML frontmatter at top).
   - Recommendation: Add `?? ''` fallback (already shown in examples above). No further action needed.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Node.js | Astro build | Yes | v24.14.0 | — |
| npm | Package management | Yes | 11.9.0 | — |
| Astro | Site generation | Yes | 6.0.8 | — |
| Tailwind CSS | Styling | Yes | 4.2.2 | — |

No missing dependencies. This phase is purely frontend code changes within the existing installed stack.

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (Python) for Python scripts; no JS/Astro test framework currently installed |
| Config file | `pytest.ini` at repo root |
| Quick run command | `pytest tests/ -x -q` |
| Full suite command | `pytest tests/ -v` |
| JS unit tests | None installed — see Wave 0 Gaps |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| LESS-01 | Today's lesson displayed (fallback to most recent) | unit (parser function) | `pytest tests/test_lesson_parser.py::test_featured_lesson_selection -x` | Wave 0 |
| LESS-02 | 5 recent lessons listed | unit (parser function) | `pytest tests/test_lesson_parser.py::test_recent_lessons_list -x` | Wave 0 |
| LESS-03 | Notice bar shown when today absent | unit (parser function) | `pytest tests/test_lesson_parser.py::test_notice_bar_condition -x` | Wave 0 |
| LESS-04 | Article text always visible | manual / visual | Manual UAT — no automated structural test | N/A |
| LESS-05 | Vocabulary collapse/expand | manual / visual | Manual UAT — collapse behavior is runtime JS | N/A |
| LESS-06 | Expressions collapse/expand | manual / visual | Manual UAT | N/A |
| LESS-07 | Comprehension collapse/expand | manual / visual | Manual UAT | N/A |
| LESS-08 | Tap-to-reveal Q&A answers | manual / visual | Manual UAT — runtime JS behavior | N/A |
| LESS-09 | Mobile sizing (≥16px text, ≥44px targets) | manual / visual | Manual UAT — verify in browser DevTools mobile view | N/A |

**Note on JS testing:** The interactive behaviors (LESS-04 through LESS-09) are implemented as `is:inline` vanilla JS. These are best verified via manual UAT or an e2e framework (Playwright). Installing Playwright adds significant complexity. Given the project is simple static pages, manual UAT is appropriate for this phase. The planner should include explicit UAT steps for LESS-04 through LESS-09.

**Note on unit-testable logic:** The parsing functions (`parseSections`, `extractSourceUrl`, `extractPreview`, `parseComprehension`) are pure TypeScript functions that can be extracted to a utility module and tested. However, the project has no JS test runner. Options:
1. Write tests in Python (mock the string inputs) — not idiomatic.
2. Accept manual testing of parser output — pragmatic for this phase.
3. Add Vitest (zero-config JS test runner that works with Astro/TS).

**Recommendation:** Add Vitest as a devDependency in Wave 0 to enable unit-testing the pure parser functions. This aligns with the project's `nyquist_validation: true` config and the global testing rules requiring 80% coverage.

### Sampling Rate
- **Per task commit:** `pytest tests/ -x -q` (Python tests) + manual browser check of the affected page
- **Per wave merge:** `pytest tests/ -v` + Vitest (if added) + manual mobile UAT
- **Phase gate:** Full suite green + manual UAT checklist before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `website/vitest.config.ts` — Vitest config for testing parser utilities
- [ ] `website/src/lib/lesson-parser.ts` — extracted pure parser functions (enables unit testing)
- [ ] `website/src/lib/lesson-parser.test.ts` — unit tests for `parseSections`, `extractSourceUrl`, `extractPreview`, `parseComprehension`, `getTodayShanghai`
- [ ] Install Vitest: `cd website && npm install -D vitest`

If Vitest is deemed too much for this phase: "None — parser functions verified via manual browser testing of build output."

---

## Sources

### Primary (HIGH confidence)
- Astro Content Collections docs (entry.body, render() free function) — verified against Phase 02 working code in `[id].astro`
- `content/2026-03-24.md` — exact format verified directly; all regex patterns validated against real content
- `website/package.json` — exact versions of astro, tailwindcss, @tailwindcss/vite confirmed
- `website/astro.config.mjs` — `base: '/study-all'` confirmed; `import.meta.env.BASE_URL` behavior follows from this
- Tailwind 4 docs — `@plugin` directive usage, arbitrary value syntax `transition-[grid-template-rows]`

### Secondary (MEDIUM confidence)
- `grid-template-rows` CSS transition browser support — Chrome 107+, Safari 16.4+, Firefox 110+ (from MDN/Can I Use; broadly supported as of 2026)
- `Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Shanghai' })` reliably producing `YYYY-MM-DD` — standard JS behavior, cross-verified by expected output format of `en-CA` locale

### Tertiary (LOW confidence)
- None — all critical claims verified against project files or standard APIs

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all packages confirmed from `package.json`; no new packages needed
- Architecture: HIGH — patterns validated against actual content file format; Astro API confirmed from working Phase 02 code
- Pitfalls: HIGH — most derived from concrete issues observable in the codebase (base path, timezone, Tailwind 4 no-config)
- JS animation approach: MEDIUM — `grid-template-rows` transition is supported but Tailwind 4 arbitrary value syntax needs verification at implementation time

**Research date:** 2026-03-24
**Valid until:** 2026-04-24 (30 days; stack is stable)
