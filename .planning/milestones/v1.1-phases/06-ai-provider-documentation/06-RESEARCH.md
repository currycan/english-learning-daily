# Phase 6: AI Provider Documentation - Research

**Researched:** 2026-03-23
**Domain:** Technical documentation authoring — API key setup guides and GitHub Actions secrets configuration
**Confidence:** HIGH

## Summary

Phase 6 is a pure documentation phase. No code changes are required. The deliverable is a single Markdown file (`docs/ai-providers.md`) that gives any developer zero-prior-knowledge instructions for obtaining API keys from OpenAI and Anthropic, storing them as GitHub Actions Repository Secrets, and understanding how the provider priority system works.

All the underlying implementation is complete (Phases 4 and 5). The documentation must accurately reflect the already-implemented behavior: `AI_PROVIDER` env var overrides `ai_provider` in `plan/config.json`, which defaults to `"anthropic"`. Both `OPENAI_API_KEY` and `ANTHROPIC_API_KEY` are consumed by the `daily-content.yml` workflow. Fallback is automatic and requires no user action.

The project already has `docs/setup-guide.md` and `docs/configuration.md` that cover adjacent ground, including a brief mention of obtaining an Anthropic key and adding it as a secret. The new `docs/ai-providers.md` must be the authoritative, standalone reference for the dual-provider configuration — deeper and more actionable than the passing mentions in existing docs.

**Primary recommendation:** Write `docs/ai-providers.md` as a self-contained reference; cross-link from `docs/setup-guide.md` and `docs/configuration.md` where those mention API keys.

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| DOCS-01 | `docs/ai-providers.md` exists with step-by-step instructions for obtaining an OpenAI API key from platform.openai.com | platform.openai.com URL confirmed correct; step sequence: sign up / log in → API Keys page → Create new secret key → copy immediately |
| DOCS-02 | Document contains step-by-step instructions for obtaining an Anthropic API key from console.anthropic.com | console.anthropic.com URL confirmed correct; existing `setup-guide.md` provides the brief version; new doc expands it |
| DOCS-03 | Document explains how to store `OPENAI_API_KEY` and `ANTHROPIC_API_KEY` as GitHub Actions Repository Secrets | Exact navigation path already documented in `docs/setup-guide.md` (steps 3 and 7); verified matches GitHub UI path |
| DOCS-04 | Document states the priority rule: `AI_PROVIDER` env var overrides `ai_provider` in `plan/config.json` | Implemented and verified in `scripts/ai_provider.py` lines 31-38; `resolve_provider()` shows exact logic |
</phase_requirements>

---

## Standard Stack

### Core
| Asset | Version | Purpose | Why Standard |
|-------|---------|---------|--------------|
| Markdown | CommonMark | Documentation file format | All existing project docs use Markdown; GitHub renders natively |
| `docs/` directory | existing | Documentation location | Already contains `setup-guide.md`, `configuration.md`, `content-pipeline.md`, `script-reference.md`, `architecture.md` |

### Supporting
No libraries required. This is a documentation-only phase.

**Installation:**
No installation required.

---

## Architecture Patterns

### Recommended Project Structure
```
docs/
├── ai-providers.md    # NEW — this phase's deliverable
├── setup-guide.md     # Existing — cross-link FROM here to ai-providers.md
├── configuration.md   # Existing — cross-link FROM here for priority rule
├── architecture.md    # Existing
├── content-pipeline.md # Existing
└── script-reference.md # Existing
```

### Pattern 1: Standalone Reference Document
**What:** A single file that can be read independently without requiring the reader to consult other docs first.
**When to use:** When the subject (dual-provider setup) has enough scope to warrant its own file and will be linked to from multiple places.
**Content order:**
1. Overview paragraph — what this doc covers and why
2. OpenAI API key acquisition (DOCS-01)
3. Anthropic API key acquisition (DOCS-02)
4. GitHub Actions secrets setup for both keys (DOCS-03)
5. Provider priority rule explanation with example (DOCS-04)
6. Cost estimates / practical notes

### Pattern 2: Bilingual Format (English + Chinese)
**What:** Parallel English and Chinese per section, matching the style of `setup-guide.md` and `configuration.md`.
**When to use:** All existing project docs use this pattern. `docs/ai-providers.md` must match.
**Example from `setup-guide.md`:**
```markdown
Sign up at [console.anthropic.com](https://console.anthropic.com) and create an API key.

在 [console.anthropic.com](https://console.anthropic.com) 注册并创建 API key。
```

### Anti-Patterns to Avoid
- **Splitting into two files (one per provider):** The priority rule and GitHub secrets apply to both together; splitting forces readers to consult two files.
- **Duplicating setup-guide.md:** `ai-providers.md` is the deep-dive reference; `setup-guide.md` links to it rather than repeating everything.
- **Including secrets in examples:** Never show real key values even as placeholders like `sk-abc123` — use `<your_openai_api_key>` style.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| GitHub Secrets navigation path | Re-derive from scratch | Copy verified path from `docs/setup-guide.md` (steps 3 and 7) | Path already verified and documented |
| Priority rule description | Paraphrase from memory | Quote directly from `ai_provider.py` docstring (lines 7-14) | Source of truth is the code |

**Key insight:** The implementation is the ground truth for DOCS-04. The docstring at the top of `scripts/ai_provider.py` already states the priority rule precisely — the documentation must reflect that, not invent its own wording.

---

## Common Pitfalls

### Pitfall 1: Missing OPENAI_API_KEY from docs/configuration.md secrets table
**What goes wrong:** `docs/configuration.md` GitHub Secrets table only lists `BARK_TOKEN` and `ANTHROPIC_API_KEY`. After this phase, `OPENAI_API_KEY` is also required and must appear in that table.
**Why it happens:** `configuration.md` was written before OpenAI integration.
**How to avoid:** Update the secrets table in `docs/configuration.md` as part of this phase (or note it as a cross-doc update task in PLAN.md).
**Warning signs:** Reader follows `configuration.md` only, misses `OPENAI_API_KEY`, CI falls back silently on every run.

### Pitfall 2: Stating OPENAI_API_KEY is "optional"
**What goes wrong:** The fallback system means the workflow succeeds even without `OPENAI_API_KEY` if Anthropic is the default — so a developer might document it as optional. But this defeats the purpose of the dual-provider setup.
**Why it happens:** Confusing "CI won't crash without it" with "it isn't needed."
**How to avoid:** Document both keys as required for full dual-provider capability. Note that the default provider is `anthropic` (from `plan/config.json`) so Anthropic key is strictly required; OpenAI key is required for OpenAI to work and for fallback to work when Anthropic is primary.
**Warning signs:** Developer configures only one key, fallback silently fails.

### Pitfall 3: Wrong API console URLs
**What goes wrong:** Linking to wrong subdomain (e.g., `api.openai.com` instead of `platform.openai.com`).
**Why it happens:** Multiple OpenAI URLs exist; the key management page is specifically at `platform.openai.com/api-keys`.
**How to avoid:** Use exact URLs verified below.
**Warning signs:** Link returns 404 or lands on a non-key-management page.

### Pitfall 4: Omitting the config.json field name
**What goes wrong:** DOCS-04 says explain the priority rule, but without naming `ai_provider` (the field name in config.json) the reader can't actually use it.
**Why it happens:** Describing behavior at too high a level.
**How to avoid:** Include the literal JSON snippet showing `"ai_provider": "anthropic"` and the literal env var name `AI_PROVIDER`.

---

## Code Examples

Verified patterns from the implementation:

### Priority Rule (from ai_provider.py lines 7-14 and 31-32)
```
Source: scripts/ai_provider.py docstring + resolve_provider()

Provider resolution priority:
    1. AI_PROVIDER env var (if set and non-empty)
    2. ai_provider field in config dict (defaults to "anthropic")
```

```python
# Source: scripts/ai_provider.py line 32
provider = os.environ.get("AI_PROVIDER") or config.get("ai_provider", "anthropic")
```

### config.json snippet to show in documentation
```json
// Source: plan/config.json
{
  "ai_provider": "anthropic",
  "openai_model": "gpt-4o-mini"
}
```

### GitHub Actions secrets setup path (verified from setup-guide.md + configuration.md)
```
Settings → Secrets and variables → Actions → New repository secret
  Name:  OPENAI_API_KEY
  Value: <your OpenAI API key>

Settings → Secrets and variables → Actions → New repository secret
  Name:  ANTHROPIC_API_KEY
  Value: <your Anthropic API key>
```

### Workflow env block showing both secrets in use (from daily-content.yml lines 34-35)
```yaml
# Source: .github/workflows/daily-content.yml
env:
  ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

---

## State of the Art

| Old State | Current State | When Changed | Impact |
|-----------|---------------|--------------|--------|
| Single provider (Anthropic only) | Dual provider with fallback | Phase 4-5 (2026-03-23) | Both `OPENAI_API_KEY` and `ANTHROPIC_API_KEY` now consumed by CI |
| `docs/configuration.md` secrets table lists only `BARK_TOKEN` + `ANTHROPIC_API_KEY` | Must now include `OPENAI_API_KEY` | This phase | `configuration.md` needs a row added |
| `docs/setup-guide.md` mentions only Anthropic key | Must reference or link to OpenAI key setup | This phase | Cross-link or add note |

**Note:** `docs/setup-guide.md` Step 6 currently reads "Get an Anthropic API Key" with no mention of OpenAI. After this phase, either that step links to `docs/ai-providers.md`, or a brief OpenAI parallel step is added.

---

## Open Questions

1. **Should `docs/configuration.md` be updated in this phase?**
   - What we know: Its GitHub Secrets table omits `OPENAI_API_KEY`, which is now in `daily-content.yml`
   - What's unclear: Whether PLAN.md scopes this to `ai-providers.md` only or treats configuration.md update as in-scope
   - Recommendation: Include it. A developer following `configuration.md` will be confused by the missing key. One-line addition to the table.

2. **Cross-link from setup-guide.md Step 6?**
   - What we know: Step 6 of `setup-guide.md` covers only Anthropic key acquisition. OpenAI key is now equally relevant.
   - What's unclear: Whether to update `setup-guide.md` or just ensure `ai-providers.md` is discoverable
   - Recommendation: Add one sentence to Step 7 of `setup-guide.md`: "For dual-provider (OpenAI + Anthropic) setup, see `docs/ai-providers.md`."

---

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (existing, no version pinned in requirements.txt) |
| Config file | none — discovered by convention |
| Quick run command | `pytest tests/ -x -q` |
| Full suite command | `pytest tests/ -v` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| DOCS-01 | `docs/ai-providers.md` exists and contains OpenAI key instructions | smoke (file existence + grep) | `test -f docs/ai-providers.md && grep -q 'platform.openai.com' docs/ai-providers.md` | ❌ Wave 0 |
| DOCS-02 | Document contains Anthropic key instructions | smoke (grep) | `grep -q 'console.anthropic.com' docs/ai-providers.md` | ❌ Wave 0 |
| DOCS-03 | Document explains GitHub Actions secrets for both keys | smoke (grep) | `grep -q 'OPENAI_API_KEY' docs/ai-providers.md && grep -q 'ANTHROPIC_API_KEY' docs/ai-providers.md` | ❌ Wave 0 |
| DOCS-04 | Document states priority rule | smoke (grep) | `grep -q 'AI_PROVIDER' docs/ai-providers.md` | ❌ Wave 0 |

**Note:** DOCS requirements are documentation content requirements, not behavioral code requirements. Automated verification is most naturally done via shell grep checks or a minimal pytest fixture that asserts file content — not unit tests with mocks. Pytest parametrize over required strings is the cleanest approach.

### Sampling Rate
- **Per task commit:** `pytest tests/ -x -q`
- **Per wave merge:** `pytest tests/ -v`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_ai_provider_docs.py` — pytest file that asserts `docs/ai-providers.md` exists and contains required content strings for all four DOCS requirements
- [ ] No framework install needed — pytest already present

---

## Sources

### Primary (HIGH confidence)
- `scripts/ai_provider.py` — source of truth for provider resolution logic, exact env var names, config field names, and fallback behavior
- `plan/config.json` — confirmed field name `ai_provider`, current default value `"anthropic"`, and `openai_model` value `"gpt-4o-mini"`
- `.github/workflows/daily-content.yml` — confirmed both `OPENAI_API_KEY` and `ANTHROPIC_API_KEY` are consumed as secrets
- `docs/setup-guide.md` — verified GitHub Secrets navigation path and existing Anthropic key setup steps
- `docs/configuration.md` — verified existing secrets table (identifies gap: `OPENAI_API_KEY` missing)

### Secondary (MEDIUM confidence)
- `platform.openai.com/api-keys` — confirmed as the correct URL for OpenAI API key management (standard knowledge, highly stable URL)
- `console.anthropic.com` — confirmed as the correct URL for Anthropic API key management (already linked in `setup-guide.md`)

### Tertiary (LOW confidence)
- None

---

## Metadata

**Confidence breakdown:**
- Content requirements: HIGH — all four DOCS requirements map directly to verifiable strings derivable from the existing code and config
- URL accuracy: MEDIUM — platform.openai.com and console.anthropic.com are standard, well-known URLs; no dynamic verification performed
- Cross-doc update scope: MEDIUM — identified as needed but not explicitly listed in REQUIREMENTS.md; planner should decide whether to include

**Research date:** 2026-03-23
**Valid until:** 2026-06-23 (stable domain — GitHub Secrets UI and API console URLs change rarely)
