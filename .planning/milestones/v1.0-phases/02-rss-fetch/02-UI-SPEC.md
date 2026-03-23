---
phase: 2
slug: rss-fetch
status: draft
shadcn_initialized: false
preset: none
created: 2026-03-23
---

# Phase 2 — UI Design Contract

> Visual and interaction contract for Phase 2: RSS Fetch.
> This phase has NO web frontend. The interaction surface is the CLI terminal and stdout JSON.
> All "UI" decisions here govern terminal output formatting, error message copy, and the Article Envelope schema.

---

## Design System

| Property | Value |
|----------|-------|
| Tool | none |
| Preset | not applicable |
| Component library | none — Python CLI, no web components |
| Icon library | none |
| Font | terminal monospace (system default) |

> Source: codebase scan confirmed no components.json, no Tailwind, no src/ directory. Project is pure Python + GitHub Actions. shadcn gate: not applicable.

---

## Spacing Scale

Not applicable to this phase. The script outputs raw JSON to stdout with no visual layout.

Declared values for any future logging/stderr output — use consistent indentation:

| Token | Value | Usage |
|-------|-------|-------|
| xs | 4px | not applicable |
| sm | 8px | not applicable |
| md | 16px | not applicable |
| lg | 24px | not applicable |
| xl | 32px | not applicable |
| 2xl | 48px | not applicable |
| 3xl | 64px | not applicable |

Exceptions: none — visual spacing is not a concern for this CLI-only phase.

---

## Typography

Not applicable to this phase. Output is terminal text only.

The Article Envelope JSON written to stdout uses Python's `json.dumps()` defaults: compact single-line output with no indentation.

| Role | Size | Weight | Line Height |
|------|------|--------|-------------|
| stdout JSON | system monospace | n/a | n/a |
| stderr messages | system monospace | n/a | n/a |

---

## Color

Not applicable to this phase. No visual color surface exists.

Terminal output uses no ANSI color codes — output must be pipe-safe (no control characters that break JSON parsing downstream).

| Role | Value | Usage |
|------|-------|-------|
| Dominant (60%) | n/a | Terminal background (system default) |
| Secondary (30%) | n/a | n/a |
| Accent (10%) | n/a | n/a |
| Destructive | n/a | Error paths — communicated via stderr text only, not color |

Accent reserved for: nothing — no accent color in this phase.

---

## Output Schema Contract

This section replaces a standard visual design contract. It is the binding interface specification for the Article Envelope JSON produced by `scripts/feed_article.py`.

### Article Envelope (stdout)

```json
{
  "title": "<non-empty string, article headline>",
  "body": "<string, >= 200 characters, plain text with paragraph breaks, no HTML tags>",
  "source_url": "<non-empty string, URL of the original article>"
}
```

Constraints (all must hold for a valid envelope):
- `title`: non-empty after `.strip()`
- `body`: `len(body) >= 200` after HTML stripping and whitespace normalization
- `source_url`: non-empty after `.strip()`
- No HTML tags in `body` — `<p>`, `<br>`, `<strong>`, etc. must all be removed
- No raw HTML entities in `body` — `&amp;`, `&quot;`, `&nbsp;` must be decoded via `html.unescape()`
- Paragraph breaks in `body`: single blank line (`\n\n`) between paragraphs; no triple-or-more consecutive newlines
- Output format: single-line compact JSON via `json.dumps(envelope)` + `print()` — no pretty-printing

> Source: CONTEXT.md `## Implementation Decisions — Article Envelope JSON 输出格式` and `## 文章有效性验证`

### Idempotency stdout behavior

When today's content file already exists, the script writes to stderr and exits 0 with no stdout output:
```
[feed_article] YYYY-MM-DD already exists, skipping.
```

> Source: RESEARCH.md Pattern 3 — Idempotency Check

---

## Copywriting Contract

All copy is terminal text (stderr messages). No UI strings exist for this phase.

| Element | Copy |
|---------|------|
| Primary CTA | n/a — CLI script, no CTA |
| Empty state (no feed entries) | `ERROR: No entries found in feed {url}. Trying fallback.` |
| Error: both feeds fail | `ERROR: All feeds exhausted. Could not fetch a valid article. Check feed URLs in plan/config.json.` |
| Error: validation failure (single entry) | `WARNING: Entry "{title}" failed validation (body: {N} chars). Trying next entry.` |
| Error: bozo feed parse warning | `WARNING: feed parse error for {url}: {exception}` |
| Error: config missing field | `ERROR: plan/config.json missing required field "content_feeds". Add primary_url, fallback_url, and content_topics.` |
| Idempotency skip | `[feed_article] {date} already exists, skipping.` |
| Fallback triggered | `WARNING: Primary feed failed after {N} attempts. Switching to fallback: {fallback_url}` |
| Success (debug/CI log) | (no stdout success message — stdout carries only the JSON envelope) |

Copy rules:
- `ERROR:` prefix for all `sys.exit(1)` paths — must tell the user what went wrong AND what to do next
- `WARNING:` prefix for recoverable conditions that allow processing to continue
- Square brackets `[feed_article]` prefix for informational/idempotency messages
- Never emit any message to stdout except the final JSON envelope
- All messages go to `sys.stderr`

> Source: CONTEXT.md code patterns, RESEARCH.md Pattern 5 (error path), project CLAUDE.md `sys.exit(1)` on failure requirement.

Destructive actions: none in this phase. The script is read-only (no state mutations, no file writes, no git commits). No confirmation dialog or destructive copy needed.

---

## Registry Safety

| Registry | Blocks Used | Safety Gate |
|----------|-------------|-------------|
| PyPI | feedparser==6.0.12 | version pinned in requirements.txt — no third-party shadcn registry |
| shadcn official | none | not applicable — no web frontend |

No third-party shadcn registries. No registry vetting gate required.

> Source: RESEARCH.md Standard Stack — feedparser 6.0.12 is the only new dependency; stdlib html.parser and json require no installation.

---

## Checker Sign-Off

- [ ] Dimension 1 Copywriting: PASS
- [ ] Dimension 2 Visuals: PASS
- [ ] Dimension 3 Color: PASS
- [ ] Dimension 4 Typography: PASS
- [ ] Dimension 5 Spacing: PASS
- [ ] Dimension 6 Registry Safety: PASS

**Approval:** pending
