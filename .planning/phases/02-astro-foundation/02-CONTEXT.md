# Phase 02: Astro Foundation - Context

**Gathered:** 2026-03-24
**Status:** Ready for planning

<domain>
## Phase Boundary

Scaffold the Astro site inside `website/`, wire it into CI/CD, and prove the full pipeline works — `content/*.md` files are read at build time, a minimal lesson list renders, and the site auto-deploys to GitHub Pages on every `daily-content.yml` run.

This phase does NOT deliver the full reading experience (Phase 03) or the archive calendar (Phase 04). Those phases build on top of the foundation laid here.

</domain>

<decisions>
## Implementation Decisions

### GitHub Pages Deployment
- **D-01:** Use the official GitHub Actions deployment method: `actions/upload-pages-artifact` + `actions/deploy-pages`. Requires `pages: write` and `id-token: write` permissions on the job and `github-pages` environment. User must enable "GitHub Actions" as the Pages source in repo Settings.
- **D-02:** No `gh-pages` branch — the deploy is purely via Actions artifact, no extra branch created.

### Homepage Scope (Phase 02)
- **D-03:** Phase 02 homepage shows a **minimal lesson list** — reads `content/*.md` at build time, renders a list of lesson dates with links to individual lesson pages. This proves SC-3 (content reading) end-to-end and gives Phase 03 a working foundation to build the full reading UX on top of.
- **D-04:** Individual lesson pages exist as stubs at `/lesson/YYYY-MM-DD` (route structure registered, minimal content). Phase 03 replaces these with the full reading experience.

### Build Trigger
- **D-05:** `build-and-deploy` job runs on every `daily-content.yml` trigger (daily cron + `workflow_dispatch`) via `needs: generate-content`. No conditional skip logic — always rebuild, whether or not new content was committed today. Simple and correct.

### Astro Configuration (carried from prior context)
- **D-06:** Astro 6 in `website/` subdirectory. `base: '/study-all'` in `astro.config.mjs`.
- **D-07:** Tailwind CSS 4 via `@tailwindcss/vite` plugin (NOT the deprecated `@astrojs/tailwind` integration).
- **D-08:** Content Collections with `glob()` loader and `z.object({}).passthrough()` schema (handles no-frontmatter Markdown files).
- **D-09:** `website/` is fully isolated from Python scripts — CI `build-and-deploy` job only runs Node steps inside `./website/`.

### Claude's Discretion
- Node.js version to use in CI (choose current LTS, 22.x)
- Package manager (npm — matches project conventions, no lock file churn)
- Exact `astro.config.mjs` details (integrations, output mode `static`)
- Stub lesson page content (minimal — just render the raw Markdown for now)
- Whether to add `package.json` scripts (`build`, `preview`, `dev`)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Existing Workflow (to extend)
- `.github/workflows/daily-content.yml` — Existing workflow; `build-and-deploy` job is added here after `generate-content`

### Content Format
- `content/2026-03-24.md` — Representative sample of actual Markdown format; Content Collections loader must parse this without frontmatter errors

### Project Rules
- `CLAUDE.md` — Project constraints: immutability, no secrets in code, exit non-zero on failure
- `.planning/PROJECT.md` — Project context and constraints
- `.planning/REQUIREMENTS.md` — SITE-01 through SITE-04 define the acceptance criteria for this phase

### Prior Website Context
- `.planning/website-CONTEXT.md` — Full pre-milestone decisions (tech stack, routes, content display decisions for all phases)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `content/2026-03-24.md` — Only existing lesson file; website must degrade gracefully when only one lesson exists (no "recent list" edge case to worry about)
- `.github/workflows/daily-content.yml` — The job appended here is the integration point; existing `generate-content` job becomes the prerequisite

### Established Patterns
- GitHub Actions workflows use `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true` env var — keep this in the new job
- Git identity configured per-job (`github-actions[bot]`) — not needed for build-only job
- `permissions: contents: write` on `generate-content` — `build-and-deploy` needs different permissions (`pages: write`, `id-token: write`) scoped to that job only

### Integration Points
- `content/*.md` → Astro Content Collections `glob()` loader → build-time page generation
- `website/dist/` → `actions/upload-pages-artifact` → `actions/deploy-pages` → `https://<username>.github.io/study-all/`
- Route `/lesson/YYYY-MM-DD` registered in Phase 02 as stub; Phase 03 fills in the reading UI

</code_context>

<specifics>
## Specific Ideas

- Workflow snippet the user confirmed for `build-and-deploy`:
  ```yaml
  build-and-deploy:
    needs: generate-content
    permissions:
      pages: write
      id-token: write
    environment:
      name: github-pages
      url: ${{ steps.deploy.outputs.page_url }}
    steps:
      - uses: actions/upload-pages-artifact@v3
        with: { path: ./website/dist }
      - uses: actions/deploy-pages@v4
        id: deploy
  ```
- Homepage mockup confirmed: lesson list showing `• YYYY-MM-DD → [link]` entries, minimal styling. Phase 03 replaces this layout.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 02-astro-foundation*
*Context gathered: 2026-03-24*
