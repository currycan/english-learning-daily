# Phase 02: Astro Foundation - Research

**Researched:** 2026-03-24
**Domain:** Astro 6, GitHub Pages deployment via Actions, Tailwind CSS 4, Content Collections
**Confidence:** HIGH

## Summary

Phase 02 scaffolds a static Astro 6 site inside `website/`, wires it into the existing `daily-content.yml`
workflow, and proves the end-to-end pipeline: `content/*.md` files are read at build time, a minimal lesson
list renders with stub detail pages, and the site auto-deploys to GitHub Pages on every workflow run.

All major technical decisions are locked in CONTEXT.md. The research confirms every decision is sound,
identifies the exact package versions verified against npm, and surfaces two pitfalls that the planner must
address: (1) the workflow snippet in CONTEXT.md specifics is incomplete — the `build-and-deploy` job needs
checkout + setup-node + install + build steps before the upload/deploy actions; (2) `glob()` loader
sort order is non-deterministic, so the lesson list page must explicitly sort entries by ID descending.

**Primary recommendation:** Scaffold with `npm create astro@latest` inside `website/`, configure as
documented, extend `daily-content.yml` with the full build-and-deploy job (checkout through deploy-pages),
and use `z.object({}).passthrough()` schema to accept the no-frontmatter Markdown files.

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**GitHub Pages Deployment**
- D-01: Use `actions/upload-pages-artifact` + `actions/deploy-pages`. Requires `pages: write` and
  `id-token: write` permissions on the job and `github-pages` environment. User must enable "GitHub
  Actions" as Pages source in repo Settings.
- D-02: No `gh-pages` branch — deploy is purely via Actions artifact.

**Homepage Scope (Phase 02)**
- D-03: Phase 02 homepage shows a minimal lesson list — reads `content/*.md` at build time, renders a
  list of lesson dates with links to individual lesson pages.
- D-04: Individual lesson pages exist as stubs at `/lesson/YYYY-MM-DD` (route structure registered,
  minimal content). Phase 03 replaces these with the full reading experience.

**Build Trigger**
- D-05: `build-and-deploy` job runs on every `daily-content.yml` trigger via `needs: generate-content`.
  No conditional skip — always rebuild.

**Astro Configuration**
- D-06: Astro 6 in `website/` subdirectory. `base: '/study-all'` in `astro.config.mjs`.
- D-07: Tailwind CSS 4 via `@tailwindcss/vite` plugin (NOT `@astrojs/tailwind`).
- D-08: Content Collections with `glob()` loader and `z.object({}).passthrough()` schema.
- D-09: `website/` is fully isolated from Python scripts — CI job only runs Node steps inside
  `./website/`.

### Claude's Discretion

- Node.js version in CI: Node 22.x (current LTS)
- Package manager: npm
- Exact `astro.config.mjs` details (integrations, output mode `static`)
- Stub lesson page content (minimal — just render the raw Markdown)
- Whether to add `package.json` scripts (`build`, `preview`, `dev`)

### Deferred Ideas (OUT OF SCOPE)

None — discussion stayed within phase scope.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| SITE-01 | User can access the learning website at the GitHub Pages default URL | Astro `base: '/study-all'` + deploy-pages action; verified action versions |
| SITE-02 | Website automatically rebuilds and deploys when a new `content/*.md` file is committed | `needs: generate-content` in `daily-content.yml`; full build job steps documented |
| SITE-03 | Website builds from `content/*.md` files at build time — no runtime API calls | `glob()` loader with `base: '../../content'` relative to `website/src/`; passthrough schema confirmed |
| SITE-04 | Astro project lives in `website/` subdirectory, isolated from Python scripts | Separate job with `working-directory: ./website`; confirmed no Python dependency |
</phase_requirements>

---

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| astro | 6.0.8 | Static site generator | Locked decision D-06; island architecture, file-based routing, Content Collections |
| tailwindcss | 4.2.2 | Utility CSS framework | Locked decision D-07; v4 is current; zero-config with Vite plugin |
| @tailwindcss/vite | 4.2.2 | Vite plugin for Tailwind 4 | Required for Tailwind 4 in Astro; replaces deprecated `@astrojs/tailwind` |

**Version verification:** Verified against npm registry on 2026-03-24.

```bash
npm view astro version          # 6.0.8
npm view tailwindcss version    # 4.2.2
npm view @tailwindcss/vite version  # 4.2.2
```

### GitHub Actions

| Action | Version | Purpose |
|--------|---------|---------|
| actions/checkout | v4 | Checkout repo in build job (existing workflow uses v4) |
| actions/setup-node | v4 | Install Node 22.x in build job |
| actions/upload-pages-artifact | v3 | Package `website/dist/` as Pages artifact |
| actions/deploy-pages | v4 | Deploy artifact to GitHub Pages |

Note: `upload-pages-artifact@v4` also exists (released Aug 2025). v3 is confirmed to work and is what
the user specified in CONTEXT.md specifics. Using v3 is safe.

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| zod | bundled with astro | Schema validation for Content Collections | Required for `z.object({}).passthrough()` |
| typescript | bundled with astro | Type safety | Use `.ts` extension for `content.config.ts` |

### Installation

```bash
cd website
npm create astro@latest . -- --template minimal --install --no-git
npm install tailwindcss @tailwindcss/vite
```

The `--template minimal` flag creates a bare-bones project (no blog template) suitable for a custom build.

## Architecture Patterns

### Recommended Project Structure

```
website/
├── src/
│   ├── content.config.ts      # Collection definitions (glob loader + passthrough schema)
│   ├── pages/
│   │   ├── index.astro        # Lesson list (SITE-01, SITE-03)
│   │   └── lesson/
│   │       └── [id].astro     # Stub lesson page (D-04)
│   ├── layouts/
│   │   └── Base.astro         # HTML shell with Tailwind import
│   └── styles/
│       └── global.css         # @import "tailwindcss"
├── public/                    # Static assets (empty for Phase 02)
├── astro.config.mjs
├── package.json
├── package-lock.json          # MUST be committed — withastro/action uses it for pkg manager detection
└── tsconfig.json
```

### Pattern 1: Content Collections with glob() and passthrough schema

**What:** Uses Astro's built-in `glob()` loader to read `content/*.md` files at build time. Because
these files have no YAML frontmatter, `z.object({}).passthrough()` is used to accept the raw body
without schema errors.

**When to use:** Always — this is the locked approach (D-08).

**Example:**
```typescript
// website/src/content.config.ts
// Source: https://docs.astro.build/en/guides/content-collections/
import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const lessons = defineCollection({
  loader: glob({ pattern: '*.md', base: '../../content' }),
  schema: z.object({}).passthrough(),
});

export const collections = { lessons };
```

Key details:
- `base: '../../content'` — relative to `website/src/content.config.ts`, resolves to repo root `/content/`
- Entry `id` is the filename stem: `2026-03-24.md` → id `2026-03-24`
- `body` field contains the raw Markdown string
- Sort order from `getCollection()` is non-deterministic — always sort explicitly

### Pattern 2: astro.config.mjs

**What:** Full config combining base path, Tailwind 4 Vite plugin, and static output.

```javascript
// website/astro.config.mjs
// Source: https://docs.astro.build/en/reference/configuration-reference/
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  site: 'https://andrewliebchen.github.io',   // substitute actual username
  base: '/study-all',
  output: 'static',
  vite: {
    plugins: [tailwindcss()],
  },
});
```

### Pattern 3: Lesson list page with sorted entries

**What:** Index page that reads all collection entries and renders them as a sorted list.

```astro
---
// website/src/pages/index.astro
import { getCollection } from 'astro:content';
import Base from '../layouts/Base.astro';

const entries = await getCollection('lessons');
// Sort descending by id (YYYY-MM-DD string sort is correct for ISO dates)
const lessons = entries.sort((a, b) => b.id.localeCompare(a.id));
---
<Base title="English Learning Daily">
  <ul>
    {lessons.map(lesson => (
      <li>
        <a href={`/study-all/lesson/${lesson.id}`}>{lesson.id}</a>
      </li>
    ))}
  </ul>
</Base>
```

### Pattern 4: Stub lesson page (dynamic route)

**What:** Dynamic route that renders stub content for each lesson. Phase 03 replaces this.

```astro
---
// website/src/pages/lesson/[id].astro
import { getCollection, render } from 'astro:content';
import Base from '../../../layouts/Base.astro';

export async function getStaticPaths() {
  const lessons = await getCollection('lessons');
  return lessons.map(lesson => ({
    params: { id: lesson.id },
    props: { lesson },
  }));
}

const { lesson } = Astro.props;
const { Content } = await render(lesson);
---
<Base title={lesson.id}>
  <Content />
</Base>
```

### Pattern 5: Full build-and-deploy job (complete, corrected)

**What:** The workflow snippet in CONTEXT.md specifics is incomplete. The complete job adds checkout,
setup-node, install, and build steps before the artifact upload.

```yaml
# Append to .github/workflows/daily-content.yml

  build-and-deploy:
    needs: generate-content
    runs-on: ubuntu-latest
    permissions:
      pages: write
      id-token: write
    environment:
      name: github-pages
      url: ${{ steps.deploy.outputs.page_url }}
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: '22'

      - name: Install website dependencies
        working-directory: ./website
        run: npm ci

      - name: Build Astro site
        working-directory: ./website
        run: npm run build

      - uses: actions/upload-pages-artifact@v3
        with:
          path: ./website/dist

      - uses: actions/deploy-pages@v4
        id: deploy
```

Key detail: `npm ci` (not `npm install`) for reproducible CI installs — requires `package-lock.json`
committed to repo.

### Pattern 6: Tailwind CSS 4 global setup

```css
/* website/src/styles/global.css */
@import "tailwindcss";
```

```astro
---
// website/src/layouts/Base.astro
import '../styles/global.css';
---
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{Astro.props.title}</title>
  </head>
  <body>
    <slot />
  </body>
</html>
```

Tailwind 4 does NOT require `tailwind.config.js` for basic usage — the Vite plugin handles everything.

### Anti-Patterns to Avoid

- **Using `@astrojs/tailwind` integration:** Deprecated for Tailwind 4. Use `@tailwindcss/vite` Vite plugin.
- **Using `npm install` in CI instead of `npm ci`:** `npm ci` is reproducible and faster; requires lockfile.
- **Hardcoding links without `base`:** Use Astro's `<a href="/study-all/lesson/...">` or use the `base`
  config so Astro's built-in link helpers work. In `.astro` files, `href={`${import.meta.env.BASE_URL}lesson/${id}`}` ensures base prefix is respected.
- **Storing computed state in content.config.ts:** Schema is passthrough — derive all values from the
  raw `body` string and the `id` field (filename stem).
- **Missing `package-lock.json` in git:** CI uses `npm ci` which requires the lockfile. Commit it.
- **Not calling `actions/checkout` in build-and-deploy:** The deploy job needs the repo content to run
  the Astro build. The job DOES need checkout even though it only consumes `website/`.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Markdown file discovery | Custom glob script | `glob()` loader from `astro/loaders` | Built-in, handles pattern matching, base paths, auto-generates IDs |
| HTML from Markdown | Custom parser | `render(entry)` from `astro:content` | Handles remark/rehype pipeline, returns typed `<Content />` component |
| CSS utility framework | Custom classes | Tailwind 4 via `@tailwindcss/vite` | Pre-built responsive utilities; no config file needed for basic use |
| Pages deployment | Custom rsync/gh-pages | `upload-pages-artifact` + `deploy-pages` | Official GitHub Actions; handles artifact packaging, permissions |
| Schema validation | Custom validators | `z.object({}).passthrough()` from Zod | Bundled with Astro; zero-config passthrough for no-frontmatter files |

**Key insight:** Every moving part in this phase has a first-party solution. The phase's job is wiring
them together, not building any of them.

## Common Pitfalls

### Pitfall 1: Incomplete build-and-deploy job

**What goes wrong:** The snippet in CONTEXT.md specifics shows only `upload-pages-artifact` and
`deploy-pages`. Running this job as-is will fail — there is no `website/dist/` directory to upload
because the checkout and build steps are missing.

**Why it happens:** The snippet captures only the deployment half of the job pattern.

**How to avoid:** The complete job must include: `actions/checkout@v4` → `actions/setup-node@v4` →
`npm ci` (in `./website`) → `npm run build` (in `./website`) → `upload-pages-artifact` → `deploy-pages`.

**Warning signs:** Job fails with "Error: Path does not exist" or "No such file: ./website/dist".

### Pitfall 2: Non-deterministic getCollection() sort order

**What goes wrong:** `getCollection('lessons')` returns entries in platform-dependent order. On CI
(Linux), the order may differ from local (macOS), causing inconsistent lesson list ordering.

**Why it happens:** Documented explicitly in Astro docs — "sort order of generated collections is
non-deterministic and platform-dependent."

**How to avoid:** Always call `.sort((a, b) => b.id.localeCompare(a.id))` after `getCollection()`.
ISO date strings sort lexicographically, so string sort is correct.

**Warning signs:** Lesson list order varies between local `npm run dev` and production build.

### Pitfall 3: Internal links ignore the base path

**What goes wrong:** Hardcoded links like `<a href="/lesson/2026-03-24">` work in local dev but break
on GitHub Pages where the site is served under `/study-all/`.

**Why it happens:** GitHub Pages serves the site at `username.github.io/study-all/` not at root.
`base: '/study-all'` tells Astro to prefix build output but does not automatically rewrite hardcoded
string literals in `.astro` templates.

**How to avoid:** Use template literal with `import.meta.env.BASE_URL`:
`href={`${import.meta.env.BASE_URL}lesson/${lesson.id}`}`
Or use Astro's `<a href="/lesson/${id}">` — Astro rewrites href attributes in `.astro` files automatically
when `base` is set. Verify with `npm run build` locally and inspect `dist/` output.

**Warning signs:** Links work on `localhost:4321` but 404 on GitHub Pages.

### Pitfall 4: GitHub Pages source not set to "GitHub Actions"

**What goes wrong:** Deploy job succeeds (exits 0) but the site is not accessible. GitHub Pages continues
to serve the old (empty) site or shows a 404.

**Why it happens:** Repository must be manually configured: Settings → Pages → Source → "GitHub Actions".
This is a one-time human action that cannot be done via workflow.

**How to avoid:** Document as a prerequisite step in the plan. The URL will be
`https://<username>.github.io/study-all/` only after this is enabled.

**Warning signs:** `actions/deploy-pages` succeeds, but visiting the URL returns 404.

### Pitfall 5: glob() base path from wrong reference point

**What goes wrong:** If `base` in the glob loader is resolved relative to the wrong anchor, no files
are found and `getCollection('lessons')` returns an empty array, causing a blank lesson list.

**Why it happens:** The `base` path in `glob()` is resolved relative to the project root
(`website/`), NOT relative to `src/content.config.ts`.

**How to avoid:** Use `base: '../content'` (relative to `website/` root, pointing to the repo root's
`content/` directory). Confirm with `npm run build` locally — Astro will warn if no entries are found.

**Warning signs:** `getCollection('lessons')` returns `[]`; lesson list page renders empty.

### Pitfall 6: Missing package-lock.json

**What goes wrong:** `npm ci` in the CI job fails with "npm ci can only install packages when your
package.json and package-lock.json are in sync."

**Why it happens:** `npm create astro` generates a lockfile locally but developers sometimes gitignore
it or forget to commit it.

**How to avoid:** Commit `website/package-lock.json` to the repository. Verify with
`git add website/package-lock.json`.

## Code Examples

Verified patterns from official sources:

### Content collection definition (passthrough, no-frontmatter files)
```typescript
// website/src/content.config.ts
// Source: https://docs.astro.build/en/guides/content-collections/
import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const lessons = defineCollection({
  loader: glob({ pattern: '*.md', base: '../content' }),
  schema: z.object({}).passthrough(),
});

export const collections = { lessons };
```

### Rendering a content entry
```astro
---
// Source: https://docs.astro.build/en/reference/modules/astro-content/
import { getCollection, render } from 'astro:content';

const lessons = await getCollection('lessons');
const entry = lessons[0];
const { Content } = await render(entry);
---
<Content />
```

### Tailwind 4 astro.config.mjs
```javascript
// Source: https://tailwindcss.com/docs/installation/framework-guides/astro
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  site: 'https://<username>.github.io',
  base: '/study-all',
  output: 'static',
  vite: {
    plugins: [tailwindcss()],
  },
});
```

### BASE_URL-safe internal links
```astro
<!-- Correct: Astro rewrites /lesson/... when base is set -->
<a href={`/lesson/${lesson.id}`}>{lesson.id}</a>

<!-- Also correct using env var explicitly -->
<a href={`${import.meta.env.BASE_URL}lesson/${lesson.id}`}>{lesson.id}</a>
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `@astrojs/tailwind` integration | `@tailwindcss/vite` Vite plugin | Tailwind 4 release (Jan 2025) | Old integration deprecated; new plugin has zero-config setup |
| `src/content/config.ts` | `src/content.config.ts` | Astro 5.0 | Config file location changed; old path still works but new is canonical |
| `entry.render()` method | `render(entry)` import from `astro:content` | Astro 5.0 | Free function, not method; import from module |
| `gh-pages` branch deployment | `upload-pages-artifact` + `deploy-pages` | GitHub Pages Actions GA | No extra branch; locked decision D-02 |

**Deprecated/outdated:**
- `@astrojs/tailwind`: Works for Tailwind 3, deprecated for Tailwind 4. D-07 locks us on Tailwind 4.
- `entry.render()` as a method: Replaced by `render(entry)` imported from `astro:content` in Astro 5+.

## Open Questions

1. **Exact `site` URL in astro.config.mjs**
   - What we know: Must be `https://<username>.github.io` where username is the GitHub account owner
   - What's unclear: The actual username is not in any planning file
   - Recommendation: Planner should note this as a fill-in-the-blank step; implementer reads it from
     the repo remote URL (`git remote get-url origin`)

2. **glob() base path: `'../content'` vs `'../../content'`**
   - What we know: `base` in `glob()` is resolved relative to the project root (`website/`), not to
     `src/content.config.ts`
   - What we found: The file `website/src/content.config.ts` lives in `website/src/`, but the base
     path is resolved from `website/` (the Astro project root)
   - Recommendation: Use `base: '../content'` (one level up from `website/` to repo root `content/`).
     Verify with a local `npm run build` before marking Wave 1 complete.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Node.js | Astro build | ✓ | v24.14.0 | — |
| npm | Package install | ✓ | 11.9.0 | — |
| GitHub Actions (ubuntu-latest) | CI build+deploy | ✓ (remote) | — | — |
| GitHub Pages (repo setting) | SITE-01 | Manual prereq | — | None — human must enable in repo Settings |

**Missing dependencies with no fallback:**
- GitHub Pages must be enabled in repo Settings → Pages → Source → "GitHub Actions". This is a human
  action required before the first deploy succeeds.

**Missing dependencies with fallback:**
- None.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (Python, existing) for Python scripts; no JS test framework for Phase 02 |
| Config file | `pytest.ini` at repo root |
| Quick run command | `pytest tests/ -x` |
| Full suite command | `pytest` |

Phase 02 is a frontend scaffolding phase. The acceptance criteria are verified by build success and
browser access, not by unit tests. Existing pytest suite covers Python scripts and is unaffected.

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| SITE-01 | Site accessible at GitHub Pages URL after deploy | smoke | manual — open URL in browser | N/A |
| SITE-02 | Auto-deploy on content commit | integration | `git push` + observe Actions run | N/A |
| SITE-03 | Build reads content/*.md, no runtime calls | build verification | `cd website && npm run build` exits 0, `dist/` contains lesson pages | ❌ Wave 0 |
| SITE-04 | website/ isolated from Python | structural | `cd website && npm run build` — no Python imports | ❌ Wave 0 |

### Sampling Rate

- **Per task commit:** `cd website && npm run build` (verify build exits 0, dist/ populated)
- **Per wave merge:** `pytest` (confirm Python suite still green) + `cd website && npm run build`
- **Phase gate:** Live URL accessible + GitHub Actions workflow green before `/gsd:verify-work`

### Wave 0 Gaps

- [ ] `website/` directory — does not exist yet; scaffold with `npm create astro@latest`
- [ ] `website/src/content.config.ts` — define lessons collection with glob() + passthrough schema
- [ ] `website/package-lock.json` — must be committed for `npm ci` to work in CI
- [ ] GitHub Pages enabled in repo Settings (manual human step, document in plan)

## Project Constraints (from CLAUDE.md)

| Directive | Applies To Phase 02 |
|-----------|---------------------|
| Immutability: use `copy.deepcopy`, never mutate inputs | Python only — not applicable to JS/Astro code, but Astro components are pure functions by design |
| No secrets in code: `BARK_TOKEN` from env only | No secrets in Phase 02; no env vars needed for static build |
| Derived state: do not add computed fields to `state.json` | `state.json` not touched by website; localStorage handles read progress independently |
| Exit non-zero on failure: `sys.exit(1)` on error | Python scripts only; Astro build fails loudly by default |
| All replies in Chinese | Communication language — not a code constraint |
| Tests: `pytest` from project root using `-m` | Existing Python tests unchanged; Astro has no JS test framework for Phase 02 |

## Sources

### Primary (HIGH confidence)
- `https://docs.astro.build/en/guides/content-collections/` — glob() loader, render(), passthrough schema, sort order
- `https://docs.astro.build/en/reference/modules/astro-content/` — render() API signature, getCollection
- `https://docs.astro.build/en/guides/deploy/github/` — GitHub Pages workflow, permissions, action versions
- `https://docs.astro.build/en/reference/configuration-reference/` — base, site, output, build.assets
- `https://tailwindcss.com/docs/installation/framework-guides/astro` — @tailwindcss/vite setup
- `https://github.com/withastro/action/blob/main/action.yml` — action internals (does not add .nojekyll)
- `https://raw.githubusercontent.com/actions/upload-pages-artifact/main/action.yml` — does not add .nojekyll; no Jekyll bypass needed when using artifact-based deploy
- npm registry: `npm view astro version`, `npm view tailwindcss version`, `npm view @tailwindcss/vite version`

### Secondary (MEDIUM confidence)
- `https://www.lossless.group/learn-with/issue-resolution/getting-astro-collections-to-work-on-messy-frontmatter` — passthrough + transform pattern for no-frontmatter files
- `https://github.com/vuejs/vitepress/discussions/3629` — confirmed .nojekyll not needed with artifact-based Pages deployment
- `https://github.com/marketplace/actions/astro-deploy` — withastro/action@v6 parameters (path, node-version, package-manager)

### Tertiary (LOW confidence)
- WebSearch results for glob() base path behavior with external directories — needs local verification

## Metadata

**Confidence breakdown:**
- Standard stack (Astro 6, Tailwind 4, action versions): HIGH — verified against npm registry and official GitHub Actions repos
- Architecture (content.config.ts, astro.config.mjs, CI workflow): HIGH — verified against official Astro docs
- Pitfalls (sort order, missing checkout, base path links): HIGH — sort order documented in official docs; workflow gap identified by reading action source
- glob() base path resolution: MEDIUM — official docs confirm "anywhere on filesystem" but exact `'../content'` path needs local build verification

**Research date:** 2026-03-24
**Valid until:** 2026-04-24 (Astro and Tailwind release frequently; re-verify patch versions before implementing if > 2 weeks old)
