# Phase 02: Astro Foundation - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-03-24
**Phase:** 02-astro-foundation
**Areas discussed:** GitHub Pages deploy method, Phase 02 homepage scope, Build trigger behavior

---

## GitHub Pages Deploy Method

| Option | Description | Selected |
|--------|-------------|----------|
| Official Actions method | `upload-pages-artifact` + `deploy-pages`. Requires `pages: write` + `id-token: write`, `github-pages` environment. No extra branches. Modern GitHub-native approach. | ✓ |
| gh-pages branch push | `peaceiris/actions-gh-pages` pushes dist to `gh-pages` branch. Older pattern, requires enabling Pages from branch in Settings. Creates an extra branch. | |

**User's choice:** Official Actions method
**Notes:** Confirmed the workflow snippet with `permissions: pages: write, id-token: write` and `environment: github-pages`.

---

## Phase 02 Homepage Scope

| Option | Description | Selected |
|--------|-------------|----------|
| Minimal lesson list | Reads `content/*.md` at build time, renders list of lesson dates with links. Proves SC-3 (content reading) end-to-end. Phase 03 adds full reading UX on top. | ✓ |
| Bare placeholder | Static "site works" page, no content reading. Simpler Phase 02, but Phase 03 must add content reading AND full UI together. | |

**User's choice:** Minimal lesson list
**Notes:** Confirmed mockup — `• YYYY-MM-DD → [link]` list. Individual lesson pages exist as stubs in Phase 02; Phase 03 replaces them.

---

## Build Trigger Behavior

| Option | Description | Selected |
|--------|-------------|----------|
| Always run | `build-and-deploy` runs every time `daily-content.yml` triggers, via `needs: generate-content`. Simple, no conditional logic. | ✓ |
| Only when new content landed | `generate-content` sets an output flag; `build-and-deploy` has an `if:` condition. More efficient but more complex. | |

**User's choice:** Always run
**Notes:** Confirmed `needs: generate-content` with no skip condition. One extra build/day when content already exists is acceptable.

---

## Claude's Discretion

- Node.js version (LTS 22.x)
- Package manager (npm)
- `astro.config.mjs` details (integrations, static output mode)
- Stub lesson page content (minimal raw Markdown render)

## Deferred Ideas

None.
