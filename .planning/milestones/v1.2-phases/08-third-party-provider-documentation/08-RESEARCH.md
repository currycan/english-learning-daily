# Phase 8: Third-Party Provider Documentation - Research

**Researched:** 2026-03-23
**Domain:** Technical documentation authoring (Markdown, bilingual English/Chinese)
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**文档结构**
- 新增独立的 **Section 5: Third-Party Claude API / 第三方 Claude 兼容 API**，插入在现有 Section 4（Provider Priority Rule）之后、Summary 之前
- Section 5 内容自包含：env var 说明、config.json 示例、GitHub Secrets 步骤全部写在该节内
- 不修改 Section 3（Add Keys as GitHub Actions Secrets），保持其聚焦于核心 API key（`ANTHROPIC_API_KEY`、`OPENAI_API_KEY`）

**第三方提供商描述**
- 保持**通用描述**——「任何兼容 Claude API 的第三方端点」（any Claude-compatible third-party API endpoint）
- 不提及具体提供商名称，避免隐性背书，保持文档长期有效

**GitHub Secrets 说明位置**
- `ANTHROPIC_BASE_URL` 和 `ANTHROPIC_AUTH_TOKEN` 的 GitHub Secrets 添加步骤**仅出现在 Section 5 内部**
- 沿用 Section 3 现有的格式：`Settings → Secrets and variables → Actions → New repository secret` 代码块

**Summary 表**
- 在末尾 Summary 表新增两行，标注 **optional**：
  - `ANTHROPIC_BASE_URL (optional)` — 第三方 Claude 端点 URL
  - `ANTHROPIC_AUTH_TOKEN (optional)` — 第三方端点的 auth token
- 与现有两行保持相同列格式（Secret | Required By）

### Claude's Discretion
- Section 5 内部小节标题的具体措辞
- config.json 示例中 placeholder 值的写法（如 `"https://your-provider.example.com/v1"` 之类）
- 中文措辞的具体表达

### Deferred Ideas (OUT OF SCOPE)
无——讨论范围保持在 Phase 8 文档边界内。
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| DOCS-01 | docs/ai-providers.md includes third-party provider setup section (bilingual Chinese/English format) | Confirmed: existing doc uses English paragraph + immediate Chinese paragraph pattern throughout; same pattern must apply to Section 5 |
| DOCS-02 | docs/ai-providers.md config.json example shows anthropic_base_url and anthropic_auth_token fields | Confirmed: `generate_exercises.py` reads `config.get("anthropic_base_url")` and `config.get("anthropic_auth_token")`; Section 4 already has a JSON code block as the model to follow |
| DOCS-03 | docs/ai-providers.md GitHub Secrets section explains adding custom base_url and token as secrets | Confirmed: CI workflow already has `ANTHROPIC_BASE_URL: ${{ secrets.ANTHROPIC_BASE_URL }}` and `ANTHROPIC_AUTH_TOKEN: ${{ secrets.ANTHROPIC_AUTH_TOKEN }}`; Section 3 format is the template |
</phase_requirements>

---

## Summary

Phase 8 is a pure documentation task. All code implementation (Phase 7) is complete: `call_claude()` in `scripts/ai_provider.py` already reads `ANTHROPIC_BASE_URL` and `ANTHROPIC_AUTH_TOKEN` from env vars (highest priority) or from `model_config["anthropic_base_url"]` / `model_config["anthropic_auth_token"]` (lower priority, sourced from `plan/config.json`). The GitHub Actions workflow already injects both secrets. Nothing in the implementation needs to change.

The task is to extend `docs/ai-providers.md` with one new section (Section 5) and two new rows in the existing Summary table. The file already has a well-established bilingual format: each paragraph of English is immediately followed by its Chinese translation. Every existing section uses the same `---` horizontal rule separator. Section 3 provides the exact GitHub Secrets code block format to reuse; Section 4 provides the exact `config.json` code block format to reuse.

The only decisions left to Claude's discretion are sub-section heading wording, placeholder values in the config.json example, and Chinese phrasing.

**Primary recommendation:** Extend `docs/ai-providers.md` in-place. Insert Section 5 between Section 4's closing `---` and the `## Summary` heading. Append two optional rows to the Summary table. No other files need touching.

---

## Standard Stack

### Core

| Library / Tool | Version | Purpose | Why Standard |
|----------------|---------|---------|--------------|
| Markdown | — | Documentation format | Already used throughout the project |
| JSON code blocks | — | Configuration examples | Established pattern in Section 4 |
| Plain-text code blocks | — | GitHub Secrets navigation paths | Established pattern in Section 3 |

No new libraries or dependencies. This phase produces only a Markdown file edit.

**Installation:** None required.

---

## Architecture Patterns

### Existing File Structure to Preserve

```
docs/ai-providers.md
├── Overview / 概述
├── ## 1. Get an OpenAI API Key
├── ## 2. Get an Anthropic API Key
├── ## 3. Add Keys as GitHub Actions Secrets
├── ## 4. Provider Priority Rule       ← existing last section before Summary
├── [NEW] ## 5. Third-Party Claude API ← INSERT HERE
└── ## Summary / 配置总结              ← append 2 rows here
```

### Pattern 1: Bilingual Paragraph Format

**What:** Every English sentence or paragraph is immediately followed by its Chinese translation. No separate English/Chinese sections — they interleave at the paragraph level.

**When to use:** All prose in Section 5.

**Example (from existing Section 3):**
```markdown
Both `OPENAI_API_KEY` and `ANTHROPIC_API_KEY` must be added as GitHub Repository Secrets so the CI workflow can access them. Neither key is stored in code or config files.

两个密钥 `OPENAI_API_KEY` 和 `ANTHROPIC_API_KEY` 均须添加为 GitHub 仓库 Secret，以便 CI 工作流访问。两者均不存储在代码或配置文件中。
```

**Source:** `docs/ai-providers.md` — observed throughout the file.

### Pattern 2: GitHub Secrets Code Block Format

**What:** Plain (no language tag) code block showing the navigation path and Name/Value fields.

**When to use:** Documenting each secret to add.

**Example (from existing Section 3):**
```markdown
```
Settings → Secrets and variables → Actions → New repository secret
  Name:  OPENAI_API_KEY
  Value: <your OpenAI API key>
```
```

**Source:** `docs/ai-providers.md` Section 3.

### Pattern 3: JSON Config Example Format

**What:** JSON code block showing the relevant fields with realistic placeholder values.

**When to use:** Documenting config.json optional fields.

**Example (from existing Section 4):**
```markdown
```json
{
  "ai_provider": "anthropic",
  "openai_model": "gpt-4o-mini"
}
```
```

**Source:** `docs/ai-providers.md` Section 4.

### Pattern 4: Summary Table Row Format

**What:** Pipe-delimited Markdown table with `Secret / 密钥` and `Required By / 所需功能` columns.

**When to use:** Adding the two optional secrets to the Summary table.

**Existing rows:**
```markdown
| Secret / 密钥 | Required By / 所需功能 |
|---|---|
| `ANTHROPIC_API_KEY` | Default provider (`anthropic`); fallback when OpenAI is primary |
| `OPENAI_API_KEY` | Required when `AI_PROVIDER=openai` or as fallback for Anthropic |
```

New rows to append (wording is Claude's discretion):
```markdown
| `ANTHROPIC_BASE_URL` (optional) | Third-party Claude-compatible endpoint URL / 第三方 Claude 兼容端点 URL |
| `ANTHROPIC_AUTH_TOKEN` (optional) | Auth token for third-party endpoint / 第三方端点认证 token |
```

**Source:** `docs/ai-providers.md` Summary section.

### Anti-Patterns to Avoid

- **Separate EN/ZH sections:** The existing doc interleaves translations at the paragraph level. Do not create a "Chinese Translation" sub-section.
- **Naming a specific provider:** Locked decision — keep descriptions generic ("any Claude-compatible third-party endpoint").
- **Putting Secrets steps outside Section 5:** Locked decision — Section 3 stays as-is.
- **Adding fields to plan/config.json:** The file already supports these fields at the code level; no changes needed there.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Bilingual formatting | Custom interleave scheme | Copy existing doc pattern exactly | Consistency with sections 1-4 |
| Config example | Write from scratch | Model on Section 4's existing JSON block | Keeps examples visually consistent |
| Secrets steps | New navigation format | Reuse Section 3's code block format verbatim | Reduces cognitive load for readers |

---

## Common Pitfalls

### Pitfall 1: Priority Order Misstated

**What goes wrong:** Documenting env vars and config.json without making the priority clear.

**Why it happens:** The two sources look symmetrical but have a strict precedence: env vars always win, config.json is lower priority.

**How to avoid:** State explicitly — env vars (`ANTHROPIC_BASE_URL`, `ANTHROPIC_AUTH_TOKEN`) take highest priority; `plan/config.json` fields are the lower-priority fallback.

**Source confirmation:** `ai_provider.py` line 55-56:
```python
effective_url = os.environ.get("ANTHROPIC_BASE_URL") or base_url or ""
effective_key = os.environ.get("ANTHROPIC_AUTH_TOKEN") or auth_token or ""
```

### Pitfall 2: Empty-String Behavior Not Documented

**What goes wrong:** User sets GitHub Secret to an empty string and is confused when it is ignored.

**Why it happens:** GitHub Actions returns `""` for secrets that exist but have no value. The code treats `""` as absent (the `or` chain skips empty strings).

**How to avoid:** Note that unset or empty secrets are treated as absent — the standard Anthropic SDK defaults apply in that case.

### Pitfall 3: Inconsistent Section Numbering

**What goes wrong:** New section is labeled `## 5.` but the existing Summary section does not have a number, creating visual inconsistency.

**How to avoid:** Check that existing sections 1-4 all use the `## N. Title / 标题` format. Confirm Summary has no number — `## Summary / 配置总结` — so Section 5 gets a number but Summary keeps its unnumbered heading.

**Source confirmation:** All sections 1-4 in `docs/ai-providers.md` use the numbered format; Summary does not.

### Pitfall 4: config.json Example Showing Only New Fields

**What goes wrong:** Config example shows only `anthropic_base_url` and `anthropic_auth_token` in isolation, making it look like a complete replacement for the existing config.

**How to avoid:** Show the new fields merged into the existing config structure, with existing fields present, so it is clear these are additive optional fields.

---

## Code Examples

### Exact Variable Names (verified from source)

```python
# Source: scripts/ai_provider.py lines 55-56
effective_url = os.environ.get("ANTHROPIC_BASE_URL") or base_url or ""
effective_key = os.environ.get("ANTHROPIC_AUTH_TOKEN") or auth_token or ""
```

Env var names to document: `ANTHROPIC_BASE_URL`, `ANTHROPIC_AUTH_TOKEN`

### Exact Config Field Names (verified from source)

```python
# Source: scripts/generate_exercises.py lines 136-137
"anthropic_base_url": config.get("anthropic_base_url"),
"anthropic_auth_token": config.get("anthropic_auth_token"),
```

Config.json field names to document: `anthropic_base_url`, `anthropic_auth_token`

### Exact GitHub Actions Injection (verified from source)

```yaml
# Source: .github/workflows/daily-content.yml lines 35-36
ANTHROPIC_BASE_URL: ${{ secrets.ANTHROPIC_BASE_URL }}
ANTHROPIC_AUTH_TOKEN: ${{ secrets.ANTHROPIC_AUTH_TOKEN }}
```

GitHub Secret names to document: `ANTHROPIC_BASE_URL`, `ANTHROPIC_AUTH_TOKEN`

### Recommended config.json Example for Section 5

Show new fields merged into existing config (additive, not replacement):

```json
{
  "ai_provider": "anthropic",
  "openai_model": "gpt-4o-mini",
  "anthropic_base_url": "https://your-provider.example.com/v1",
  "anthropic_auth_token": "your-provider-auth-token"
}
```

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (detected: `pytest.ini` / `tests/` directory present) |
| Config file | `pytest.ini` or implicit (no explicit config found — pytest discovers `tests/`) |
| Quick run command | `pytest tests/test_ai_provider_docs.py -v` |
| Full suite command | `pytest` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| DOCS-01 | Section 5 present in docs/ai-providers.md with bilingual content | unit (doc content) | `pytest tests/test_ai_provider_docs.py -v -k "third_party"` | ❌ Wave 0 — new tests needed |
| DOCS-02 | anthropic_base_url and anthropic_auth_token appear in a config.json example | unit (doc content) | `pytest tests/test_ai_provider_docs.py -v -k "config"` | ❌ Wave 0 — new tests needed |
| DOCS-03 | ANTHROPIC_BASE_URL and ANTHROPIC_AUTH_TOKEN appear in a GitHub Secrets section | unit (doc content) | `pytest tests/test_ai_provider_docs.py -v -k "secrets"` | ❌ Wave 0 — new tests needed |

**Note:** `tests/test_ai_provider_docs.py` already exists but only covers DOCS-01 through DOCS-04 for the *original* provider documentation (OpenAI/Anthropic API keys, AI_PROVIDER env var). New test functions must be added to the same file to cover the v1.2 DOCS requirements.

### Sampling Rate

- **Per task commit:** `pytest tests/test_ai_provider_docs.py -v`
- **Per wave merge:** `pytest`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps

- [ ] `tests/test_ai_provider_docs.py` — add new test functions for DOCS-01 (third-party section present), DOCS-02 (config fields present), DOCS-03 (GitHub Secrets for custom vars present). The file exists; new functions are additive.

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Single-provider docs | Bilingual multi-provider docs | Phase 6 | Established the format to extend |
| No third-party support | ANTHROPIC_BASE_URL / ANTHROPIC_AUTH_TOKEN | Phase 7 | Code is done; docs pending |

**Deprecated/outdated:**
- Nothing deprecated. This phase extends existing documentation only.

---

## Open Questions

1. **Placeholder token value in config.json example**
   - What we know: The `auth_token` field maps to `api_key` in the Anthropic SDK constructor
   - What's unclear: Whether to use a realistic-looking placeholder like `"sk-ant-..."` format or a generic `"your-provider-auth-token"`
   - Recommendation: Use generic `"your-provider-auth-token"` — avoids suggesting Anthropic key format applies to all third-party providers

2. **Sub-section headings inside Section 5**
   - What we know: Sections 1-2 use numbered step lists; Section 3 uses `### Add OPENAI_API_KEY` sub-headings; Section 4 uses `### Config file default` sub-headings
   - What's unclear: Which sub-heading style fits Section 5 best
   - Recommendation: Follow Section 4 style (`### Option 1: Environment Variables`, `### Option 2: config.json`, `### Add to GitHub Secrets`) — matches the multi-option nature of third-party config

---

## Sources

### Primary (HIGH confidence)

- `docs/ai-providers.md` — full file read; establishes all formatting patterns to replicate
- `scripts/ai_provider.py` — verified exact env var names (`ANTHROPIC_BASE_URL`, `ANTHROPIC_AUTH_TOKEN`), kwarg names (`base_url`, `auth_token`), and priority logic
- `scripts/generate_exercises.py` — verified exact config.json field names (`anthropic_base_url`, `anthropic_auth_token`)
- `.github/workflows/daily-content.yml` — verified exact GitHub Secret names injected into the generate step
- `plan/config.json` — verified existing config structure that the new fields extend
- `tests/test_ai_provider_docs.py` — verified test pattern and confirmed Wave 0 gaps

### Secondary (MEDIUM confidence)

- `.planning/phases/08-third-party-provider-documentation/08-CONTEXT.md` — locked decisions from user discussion session
- `.planning/REQUIREMENTS.md` — acceptance criteria for DOCS-01, DOCS-02, DOCS-03

### Tertiary (LOW confidence)

None — all findings are grounded in direct file reads.

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — documentation only, no new libraries
- Architecture: HIGH — patterns read directly from the file being extended
- Pitfalls: HIGH — derived from reading the actual implementation code

**Research date:** 2026-03-23
**Valid until:** Stable indefinitely — this is documentation of already-implemented code; no external dependencies
