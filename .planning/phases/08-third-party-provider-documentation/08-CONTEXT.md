# Phase 8: Third-Party Provider Documentation - Context

**Gathered:** 2026-03-23
**Status:** Ready for planning

<domain>
## Phase Boundary

更新 `docs/ai-providers.md`，新增第三方 Claude 兼容 API 的配置指南，涵盖 env var、`config.json` 字段和 GitHub Secrets 三种方式。文档格式沿用已有的英中双语风格。代码实现（Phase 7）已完成，本 Phase 仅为文档补充。

</domain>

<decisions>
## Implementation Decisions

### 文档结构
- 新增独立的 **Section 5: Third-Party Claude API / 第三方 Claude 兼容 API**，插入在现有 Section 4（Provider Priority Rule）之后、Summary 之前
- Section 5 内容自包含：env var 说明、config.json 示例、GitHub Secrets 步骤全部写在该节内
- 不修改 Section 3（Add Keys as GitHub Actions Secrets），保持其聚焦于核心 API key（`ANTHROPIC_API_KEY`、`OPENAI_API_KEY`）

### 第三方提供商描述
- 保持**通用描述**——「任何兼容 Claude API 的第三方端点」（any Claude-compatible third-party API endpoint）
- 不提及具体提供商名称，避免隐性背书，保持文档长期有效

### GitHub Secrets 说明位置
- `ANTHROPIC_BASE_URL` 和 `ANTHROPIC_AUTH_TOKEN` 的 GitHub Secrets 添加步骤**仅出现在 Section 5 内部**
- 沿用 Section 3 现有的格式：`Settings → Secrets and variables → Actions → New repository secret` 代码块

### Summary 表
- 在末尾 Summary 表新增两行，标注 **optional**：
  - `ANTHROPIC_BASE_URL (optional)` — 第三方 Claude 端点 URL
  - `ANTHROPIC_AUTH_TOKEN (optional)` — 第三方端点的 auth token
- 与现有两行保持相同列格式（Secret | Required By）

### Claude's Discretion
- Section 5 内部小节标题的具体措辞
- config.json 示例中 placeholder 值的写法（如 `"https://your-provider.example.com/v1"` 之类）
- 中文措辞的具体表达

</decisions>

<canonical_refs>
## Canonical References

**下游 Agent 在规划或实现前必须读取以下文件。**

### 需要修改的文档
- `docs/ai-providers.md` — 当前文档完整内容，新内容追加至此文件

### 需求来源
- `.planning/REQUIREMENTS.md` — DOCS-01、DOCS-02、DOCS-03 的具体验收标准

### Phase 7 实现参考（了解已实现的字段/参数名）
- `scripts/ai_provider.py` — `call_claude(base_url, auth_token)` 参数名，env var 名称（`ANTHROPIC_BASE_URL`、`ANTHROPIC_AUTH_TOKEN`）
- `scripts/generate_exercises.py` — `model_config` 中的 `anthropic_base_url`、`anthropic_auth_token` 字段名
- `.github/workflows/daily-content.yml` — CI workflow 中已添加的 env var 注入方式

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `docs/ai-providers.md` — 已有英中双语结构和排版惯例，直接扩展，不新建文件

### Established Patterns
- **英中双语格式**：每段英文后紧跟中文译文，对照排版（来自 Phase 6 决策）
- **GitHub Secrets 代码块格式**：`Settings → Secrets and variables → ...` 纯文本 code block，见 Section 3 现有示例
- **Config.json 示例格式**：JSON 代码块，key 使用 snake_case，见 Section 4 现有示例

### Integration Points
- `docs/ai-providers.md` Section 4 之后插入新 Section 5
- `docs/ai-providers.md` Summary 表追加两行（optional 标注）

</code_context>

<specifics>
## Specific Ideas

无特殊要求——沿用现有文档风格即可。

</specifics>

<deferred>
## Deferred Ideas

无——讨论范围保持在 Phase 8 文档边界内。

</deferred>

---

*Phase: 08-third-party-provider-documentation*
*Context gathered: 2026-03-23*
