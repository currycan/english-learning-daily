# Architecture Research

**Domain:** Astro static site integrated with GitHub Actions content pipeline
**Researched:** 2026-03-24
**Confidence:** HIGH (all critical decisions verified against official Astro docs and GitHub Actions docs)

## Standard Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                  GITHUB ACTIONS  daily-content.yml                   │
│                                                                       │
│  job: generate-content          job: build-and-deploy               │
│  ┌────────────────────────┐     ┌──────────────────────────────┐    │
│  │ 06:00 BJT cron trigger │     │ needs: generate-content      │    │
│  │  feed_article.py       │     │ if: success                  │    │
│  │  generate_exercises.py │────▶│  actions/checkout ref: main  │    │
│  │  commit_content.py     │     │  withastro/action path:      │    │
│  │  → content/YYYY-MM-DD  │     │    website                   │    │
│  │    .md pushed to main  │     │  actions/deploy-pages@v4     │    │
│  └────────────────────────┘     └──────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
                                           │
                                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│              ASTRO BUILD  (website/ subdirectory)                    │
│                                                                       │
│  src/content/config.ts                                               │
│  ┌─────────────────────────────────────────────────────────┐        │
│  │  glob({ pattern: "**/*.md", base: "../../content" })    │        │
│  │  → lessons collection (one entry per YYYY-MM-DD.md)     │        │
│  └─────────────────────────────────────────────────────────┘        │
│           │  getCollection("lessons") at build time                   │
│           ▼                                                           │
│  ┌──────────────┐  ┌───────────────────┐  ┌──────────────────┐      │
│  │ index.astro  │  │lesson/[date].astro│  │  archive.astro   │      │
│  │  Today full  │  │ Article (visible) │  │  Calendar grid   │      │
│  │  Recent list │  │ Vocab (collapsed) │  │  Read/unread via │      │
│  └──────────────┘  │ Chunks (collapsed)│  │  localStorage    │      │
│                    │ Q&A (tap-reveal)  │  └──────────────────┘      │
│                    └───────────────────┘                             │
└─────────────────────────────────────────────────────────────────────┘
                                           │
                                           ▼
                      https://<user>.github.io/study-all/
```

### Component Responsibilities

| Component | Responsibility | Location |
|-----------|---------------|----------|
| `generate-content` job | Daily content generation; commits `content/YYYY-MM-DD.md` | `.github/workflows/daily-content.yml` (existing, unchanged) |
| `build-and-deploy` job | Astro build after content commit; deploys to Pages | `.github/workflows/daily-content.yml` (new job added) |
| `src/content/config.ts` | Defines `lessons` collection via glob loader pointing at `../../content/` | `website/src/content/config.ts` |
| `pages/index.astro` | Homepage: today's lesson full-width + recent list (last 5-7) | `website/src/pages/index.astro` |
| `pages/lesson/[date].astro` | Static route per date; parses 4 Markdown sections, renders with components | `website/src/pages/lesson/[date].astro` |
| `pages/archive.astro` | Calendar grid; all lesson dates from collection; read state from localStorage | `website/src/pages/archive.astro` |
| `lib/parseLesson.ts` | Splits raw Markdown body on `## ` headings into 4 typed section strings | `website/src/lib/parseLesson.ts` |
| `layouts/Base.astro` | HTML shell; theme detection script runs before first paint to prevent FOUC | `website/src/layouts/Base.astro` |
| Theme (localStorage) | Dark/light toggle persisted in browser; no server involvement | Inline `<script>` in `Base.astro` |
| Read progress (localStorage) | Tracks read dates; calendar reads on mount; set on lesson page load | Inline `<script>` in `[date].astro` and `archive.astro` |

## Recommended Project Structure

```
study-all/
├── content/                       # Existing: YYYY-MM-DD.md files (untouched by website)
├── scripts/                       # Existing: Python pipeline (untouched)
├── .github/
│   └── workflows/
│       └── daily-content.yml      # Modified: add build-and-deploy job
└── website/                       # New: Astro project root (isolated from Python)
    ├── astro.config.mjs           # site + base config for GitHub Pages
    ├── package.json
    ├── tsconfig.json
    └── src/
        ├── content/
        │   └── config.ts          # Lessons collection (glob loader)
        ├── pages/
        │   ├── index.astro        # Homepage
        │   ├── archive.astro      # Calendar view
        │   └── lesson/
        │       └── [date].astro   # Dynamic per-lesson route
        ├── components/
        │   ├── LessonContent.astro   # Orchestrates section rendering
        │   ├── VocabCard.astro       # Single vocabulary entry
        │   ├── ChunkCard.astro       # Single chunking expression entry
        │   ├── QAItem.astro          # Single Q+A with tap-to-reveal
        │   └── CalendarGrid.astro    # Month calendar with read state
        ├── layouts/
        │   └── Base.astro         # HTML shell, theme script, meta tags
        └── styles/
            └── global.css         # CSS custom properties for dark/light theme
```

### Structure Rationale

- **`website/` as subdirectory (not repo root):** Keeps Astro tooling (`node_modules/`, `package.json`, `dist/`) isolated from the Python project. All `npm` and `astro build` commands use `working-directory: website` in CI. No `package.json` collision at root.
- **`src/content/config.ts` with glob loader at `../../content/`:** Astro v5 Content Layer API supports `base` paths outside `src/`, so the existing `content/` directory is consumed directly at build time. No copying, no symlinking, no intermediate manifest file.
- **No JSON manifest generation step:** The glob loader replaces the "generate JSON manifest" idea mentioned in website-CONTEXT.md (D-05). `getCollection("lessons")` returns all entries typed and sorted — the manifest approach is unnecessary.
- **One component per content type:** `VocabCard`, `ChunkCard`, `QAItem` are small, focused components. They receive pre-parsed string segments, not raw Markdown. This keeps the Astro components simple and the parsing logic isolated in `parseLesson.ts`.

## Architectural Patterns

### Pattern 1: Same-workflow sequential jobs (content then build)

**What:** Add a `build-and-deploy` job to `daily-content.yml` using `needs: generate-content`. The Astro build runs immediately after the content job, in the same workflow run.

**When to use:** Always for this project. Content generation and site deployment are one logical operation triggered by the same schedule.

**Trade-offs:** Simpler than `workflow_run` — no cross-workflow event propagation, no separate workflow file, inherits skip behavior when the idempotent guard fires. One workflow to monitor in the Actions tab.

**Example:**
```yaml
# Addition to .github/workflows/daily-content.yml

  build-and-deploy:
    needs: generate-content
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pages: write
      id-token: write
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - uses: actions/checkout@v4
        with:
          ref: main          # Re-checkout after content commit lands
      - uses: withastro/action@v3
        with:
          path: website      # Astro project is in website/ subdirectory
      - uses: actions/deploy-pages@v4
        id: deployment
```

**Critical detail:** The `build-and-deploy` job must use `actions/checkout@v4` with `ref: main` (or the default branch name). Without this, the checkout may use a stale workspace snapshot from before the content commit. The new `.md` file must be present for the glob loader to pick it up.

### Pattern 2: Astro v5 Content Layer glob loader for `content/*.md`

**What:** Define a `lessons` collection in `src/content/config.ts` using Astro's built-in `glob()` loader. The loader scans `../../content/` at build time and produces typed, queryable collection entries.

**When to use:** Always for this project. The glob loader is the canonical Astro v5 approach for local filesystem content.

**Trade-offs:** Requires Astro v5+. The `id` of each entry is automatically the filename stem (`2026-03-24`), which maps directly to the route `/lesson/2026-03-24`. No extra ID logic needed.

**Example:**
```typescript
// website/src/content/config.ts
import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const lessons = defineCollection({
  loader: glob({
    pattern: '**/*.md',
    base: '../../content',   // relative to website/ project root
  }),
  // No YAML frontmatter in existing files — use empty passthrough schema
  schema: z.object({}).passthrough(),
});

export const collections = { lessons };
```

Query in pages:
```typescript
import { getCollection } from 'astro:content';
const lessons = await getCollection('lessons');
const sorted = lessons.sort((a, b) => b.id.localeCompare(a.id));
// sorted[0].id === "2026-03-24" (most recent)
// sorted[0].body === full raw Markdown string
```

**Important constraint:** The existing Markdown files have no YAML frontmatter. The schema must use `.passthrough()` or an empty object — do not define required frontmatter fields or the collection build will fail.

### Pattern 3: Build-time Markdown section splitting via TypeScript parser

**What:** Parse the raw `body` string in `[date].astro` using a lightweight TypeScript function that splits on `## ` heading lines. No remark plugin, no MDX transformation.

**When to use:** For this project specifically. The 4 sections have fixed emoji-prefixed headings and predictable structure. A targeted string split is simpler than a full remark AST traversal.

**Why not a remark plugin:** Remark plugins transform the full document AST at collection-build time and produce one rendered HTML blob. That blob cannot be split into 4 separate strings to pass into 4 different Astro components with different interactivity (collapsible, tap-to-reveal). The section split must happen at the page rendering layer, not at the content collection layer.

**Example:**
```typescript
// website/src/lib/parseLesson.ts
export interface LessonSections {
  article: string;
  vocabulary: string;
  chunks: string;
  comprehension: string;
}

export function parseLesson(body: string): LessonSections {
  // Split on any "## " at line start, keeping prefix for identification
  const parts = body.split(/(?=^## )/m);
  const find = (emoji: string): string =>
    parts.find(p => p.startsWith(`## ${emoji}`))
      ?.replace(/^##[^\n]+\n/, '')   // strip the heading line itself
      .trim() ?? '';
  return {
    article:       find('📖'),
    vocabulary:    find('📚'),
    chunks:        find('🔗'),
    comprehension: find('❓'),
  };
}
```

Each section string is passed to a dedicated Astro component (`VocabCard`, `ChunkCard`, `QAItem`) for rendering. The components parse their section string further (splitting on `**word**` patterns etc.) using inline TypeScript logic.

### Pattern 4: GitHub Pages via `withastro/action` + `actions/deploy-pages`

**What:** Use `withastro/action@v3` (the current version, maintained by the Astro team) to build and upload the site artifact, then `actions/deploy-pages@v4` to deploy. This is the approach from Astro's official GitHub Pages deployment guide.

**When to use:** Always for Astro + GitHub Pages. The official action handles Node.js setup, dependency installation, and build path configuration automatically.

**Configuration:**
```javascript
// website/astro.config.mjs
import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://<username>.github.io',
  base: 'study-all',   // repo name — produces /study-all/ path prefix
});
```

The `base` value must match the GitHub repository name exactly (case-sensitive). Astro automatically prefixes all internal links and asset paths with this value. No manual path manipulation in component `href` attributes.

**Required repo setting:** In the GitHub repo settings under Pages, set Source to "GitHub Actions" (not "Deploy from a branch"). This one-time setting is required for `actions/deploy-pages` to work.

### Pattern 5: Collapsible sections via native `<details>` elements

**What:** Wrap vocabulary, chunks, and comprehension sections in HTML `<details>`/`<summary>` elements rather than custom JS toggle logic.

**When to use:** For the collapsible section requirement (D-14). Native `<details>` has zero JS dependency, works without JavaScript, and is accessible by default.

**Trade-offs:** Less visual flexibility than JS-driven accordions. For this project (mobile reading, simple layout) the trade-off is acceptable. Q&A tap-to-reveal (D-15) requires JS since individual answers must be hidden inside an expanded section — this is the only case needing a small `<script>` block.

**Example:**
```astro
<!-- CollapsibleSection.astro -->
<details class="section-collapsible">
  <summary>{title}</summary>
  <slot />
</details>
```

## Data Flow

### Daily Content to Live Site

```
06:00 BJT (cron)
    │
    ▼
generate-content job
    │  feed_article.py | generate_exercises.py | commit_content.py
    │  → git push: content/2026-03-24.md now on main
    │
    ▼  (needs: generate-content, after success)
build-and-deploy job
    │
    ├─ actions/checkout ref: main   ← sees new .md file
    │
    ├─ withastro/action path: website
    │     npm ci
    │     astro build
    │       glob loader scans content/*.md → lessons collection
    │       getCollection("lessons") → all entries sorted by id
    │       [date].astro generates one static HTML file per lesson
    │       index.astro: today = sorted[0], recent = sorted[1..6]
    │       archive.astro: all dates for calendar grid
    │     → dist/ built
    │
    └─ actions/deploy-pages@v4
          uploads dist/ as Pages artifact
          GitHub serves at /study-all/
```

### User Browser Flow (no server)

```
User opens https://<user>.github.io/study-all/
    │  static HTML served by GitHub Pages CDN
    ▼
index.astro output
    │  today's lesson article visible
    │  vocab/chunks/comprehension in <details> (collapsed)
    │  recent list below
    │
    ▼  user taps lesson date link
/study-all/lesson/2026-03-24
    │  static HTML
    │  on DOMContentLoaded:
    │    localStorage.setItem("read_2026-03-24", "1")
    │  Q&A answers hidden; tap "查看答案" → reveal
    │
    ▼  user opens /study-all/archive
archive.astro output
    │  calendar grid (static HTML structure)
    │  on DOMContentLoaded:
    │    read all "read_*" keys from localStorage
    │    mark matching calendar cells as read
```

### State Boundaries

```
Build-time (Astro, no runtime cost):
  getCollection("lessons")
    → sorted [{id: "YYYY-MM-DD", body: "..."}]
    → static HTML files in dist/

Client-only (localStorage, no server):
  Theme preference: "dark" | "light" | unset
    → read in <head> before first paint (prevents FOUC)
  Read progress: "read_YYYY-MM-DD" = "1" per visited lesson
    → written on lesson page load
    → read on archive page load for calendar marking
```

## Integration Points

### Existing Workflow to New Astro Build

| Connection | Mechanism | Notes |
|------------|-----------|-------|
| `generate-content` triggers `build-and-deploy` | `needs: generate-content` in same workflow file | Build job skips if content job exits early (idempotent guard) |
| `content/*.md` files to glob loader | Filesystem path `../../content` relative to `website/` | No copy step; no intermediate JSON manifest; glob reads directly |
| New commit visible to build job | `actions/checkout@v4` with `ref: main` | Without explicit `ref`, checkout may not see the just-committed file |
| GitHub Pages hosting | `environment: github-pages` + `pages: write` permission | Repo Pages setting must be set to "Source: GitHub Actions" |

### New vs Modified Files

| File | Status | Change Description |
|------|--------|--------------------|
| `.github/workflows/daily-content.yml` | Modified | Add `build-and-deploy` job with `pages: write` and `id-token: write` permissions |
| `website/` | New directory | Entire Astro project; isolated from Python scripts and tests |
| `website/astro.config.mjs` | New | `site` and `base: 'study-all'` configuration |
| `website/src/content/config.ts` | New | `lessons` collection via glob loader pointing at `../../content/` |
| `website/src/lib/parseLesson.ts` | New | Section splitter; pure TypeScript function; no Astro dependency |
| `website/src/pages/index.astro` | New | Homepage with today's lesson and recent list |
| `website/src/pages/lesson/[date].astro` | New | Static per-lesson route; calls `parseLesson`; renders 4 section components |
| `website/src/pages/archive.astro` | New | Calendar grid; client script reads localStorage for read state |
| `website/src/components/*.astro` | New | `LessonContent`, `VocabCard`, `ChunkCard`, `QAItem`, `CalendarGrid` |
| `website/src/layouts/Base.astro` | New | HTML shell with theme detection script in `<head>` |
| `content/*.md` | Unchanged | Consumed at build time, never modified by website code |
| `scripts/` (Python) | Unchanged | Content pipeline is completely decoupled from the website |

### Build Order for Implementation

Dependencies between components determine safe implementation sequence:

```
1. website/ scaffold       astro create; astro.config.mjs with site + base
2. content/config.ts       glob loader; verify getCollection returns entries
3. parseLesson.ts          pure function; unit-testable in isolation
4. [date].astro            dynamic route; validates section parsing end-to-end
5. index.astro             homepage; depends on collection sort being correct
6. archive.astro           calendar; depends on all lesson dates being available
7. Components              VocabCard, ChunkCard, QAItem, CalendarGrid
8. layouts/Base.astro      theme script; add last once page structure is stable
9. daily-content.yml       add build-and-deploy job; test via workflow_dispatch
```

## Anti-Patterns

### Anti-Pattern 1: Generating a JSON manifest as a separate CI step

**What people do:** Add a step in CI that runs `python build_manifest.py` to write `website/src/content-index.json` listing all lesson dates and titles, then `import` that JSON in Astro pages.

**Why it's wrong:** Adds a Python dependency to the Node build job. Requires the manifest to be committed or passed as an artifact between CI steps. Duplicates what Astro's glob loader already provides natively at build time. Creates a maintenance burden (schema drift between manifest and actual file structure).

**Do this instead:** Use `glob()` loader in `src/content/config.ts`. `getCollection("lessons")` at build time scans all `content/*.md` files and returns them sorted. The `id` (filename stem) is the date. No manifest needed.

### Anti-Pattern 2: Triggering site rebuild via `workflow_run` in a separate file

**What people do:** Create a separate `deploy.yml` with `on: workflow_run: workflows: ["Daily content"]` to decouple content and build workflows.

**Why it's wrong:** `workflow_run` only fires from the default branch. It adds ~30-60s latency between content commit and site rebuild. GitHub documents a hard limit of 3 workflow chain levels. When `generate-content` skips due to the idempotent guard, `workflow_run` still fires (it fires on completion, not on a new commit event), potentially triggering a redundant build. Debugging cross-workflow failures requires navigating two separate run histories.

**Do this instead:** Add `build-and-deploy` as a second job in `daily-content.yml` with `needs: generate-content`. It inherits the skip behavior naturally — if `generate-content` exits early, the downstream job can use a condition to skip the build.

### Anti-Pattern 3: Deploying via `gh-pages` branch (peaceiris/actions-gh-pages)

**What people do:** Use `peaceiris/actions-gh-pages@v3` to push the `dist/` folder to a `gh-pages` branch. Configure Pages to serve from that branch.

**Why it's wrong:** The `gh-pages` branch accumulates full build output in git history, inflating repo size permanently. Requires `contents: write` permission (broader than necessary). GitHub's own Pages infrastructure now officially prefers the artifact-based deployment (`actions/deploy-pages`). The artifact approach uses `GITHUB_TOKEN` scoped narrowly to `pages: write` — no PAT or deploy key needed.

**Do this instead:** Use `withastro/action@v3` + `actions/deploy-pages@v4`. Configure the Pages source in repo settings to "GitHub Actions". This is the approach in Astro's official documentation.

### Anti-Pattern 4: Placing the Astro project at the repository root

**What people do:** Put `astro.config.mjs`, `package.json`, and `src/` at the repo root alongside `scripts/` and `content/`.

**Why it's wrong:** `npm install` at repo root mixes Node.js tooling with the Python project. `node_modules/` conflicts with `venv/`. The default Astro `outDir` (`./dist`) lands at repo root and may be accidentally committed. Python CI steps and Astro CI steps share a working directory, which makes failures harder to isolate.

**Do this instead:** Put the Astro project in `website/`. Use `working-directory: website` for all Node/Astro CI steps. The glob loader's `base: '../../content'` path correctly reaches outside the `website/` subtree to the shared `content/` directory.

### Anti-Pattern 5: Using a remark plugin to split Markdown sections

**What people do:** Add a custom remark plugin (or `@mdxvac/remark-sectionize-headings`) to the Astro Markdown processing pipeline to wrap each `##` section in a `<section>` element.

**Why it's wrong:** Remark runs at collection build time and produces a single HTML string. That string cannot then be split into 4 independent strings to pass into 4 different Astro components with distinct interactivity (one always-visible, three collapsible, one with tap-to-reveal). The section boundaries needed for component rendering are lost once the AST is serialized to HTML.

**Do this instead:** Call `parseLesson(entry.body)` in `[date].astro` to get 4 raw Markdown strings, then pass each to its respective component. Each component handles its own rendering and interactivity.

## Scaling Considerations

This is a single-user personal learning site. Scaling is not a concern. Operational notes only:

| Concern | Current | Notes |
|---------|---------|-------|
| Astro build time | <10s for 1 file | At 365 pages/year: still <30s; glob loader is efficient |
| GitHub Pages limits | Well under 1 GB | 1 file/day at ~3 KB = ~1 MB/year of content |
| Pages deployment rate | 1/day | GitHub's limit is 100 deployments/hour; irrelevant |
| localStorage growth | 1 key/day | At 5 years = ~1,825 keys; well within 5 MB browser limit |
| `workflow_dispatch` rebuilds | On demand | Manual trigger on `daily-content.yml` rebuilds site without new content |

## Sources

- [Astro Content Collections Docs](https://docs.astro.build/en/guides/content-collections/) — glob loader API, `getCollection`, schema with no frontmatter (HIGH confidence)
- [Astro GitHub Pages Deploy Guide](https://docs.astro.build/en/guides/deploy/github/) — `withastro/action`, required permissions, `base` URL configuration (HIGH confidence)
- [withastro/action GitHub repo](https://github.com/withastro/action) — current version (v3), required permissions (`pages: write`, `id-token: write`) (HIGH confidence)
- [GitHub Actions Events Docs](https://docs.github.com/actions/using-workflows/events-that-trigger-workflows) — `workflow_run` limitations, 3-chain limit, fires-on-completion not new-commit behavior (HIGH confidence)
- [Astro Configuration Reference](https://docs.astro.build/en/reference/configuration-reference/) — `site` and `base` options for subdirectory repos (HIGH confidence)
- [remark-sectionize-headings](https://mdxvac.netlify.app/plugins/remark-sectionize-headings/) — confirmed remark plugins produce a single HTML blob, not per-section strings (MEDIUM confidence — design reasoning, not tested in isolation)
- `website-CONTEXT.md` — project decisions D-01 through D-26; used to validate recommendations against locked decisions (HIGH confidence)

---
*Architecture research for: Astro static site + GitHub Actions content pipeline integration*
*Researched: 2026-03-24*
