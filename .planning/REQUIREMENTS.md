# Requirements: English Daily Content

**Defined:** 2026-03-23
**Milestone:** v1.1 Dual AI Provider
**Core Value:** Every day a ready-to-read English lesson lands in git — real content with targeted vocabulary, chunking expressions, and exercises to deepen understanding.

## v1.1 Requirements

### Provider Abstraction

- [ ] **PRVD-01**: 系统通过统一接口调用 AI 生成内容，业务逻辑与具体提供商解耦
- [ ] **PRVD-02**: 用户可通过环境变量 `AI_PROVIDER=openai|anthropic` 切换提供商（运行时优先）
- [ ] **PRVD-03**: 用户可在 `plan/config.json` 中设置 `ai_provider` 默认值，环境变量优先级更高

### OpenAI Integration

- [ ] **OAPI-01**: 系统使用 OpenAI gpt-4o-mini 生成与现有格式完全一致的词汇、分块表达、理解问答内容
- [ ] **OAPI-02**: OpenAI 使用的模型可通过 `plan/config.json` 配置（默认 `gpt-4o-mini`）
- [ ] **OAPI-03**: `OPENAI_API_KEY` 仅从环境变量 / GitHub Secrets 读取，不写入任何代码或配置文件

### Fallback

- [ ] **FALL-01**: 主提供商 API 调用失败时，系统自动切换到备用提供商重试一次
- [ ] **FALL-02**: 两个提供商均失败时，脚本以非零退出码退出，CI 标红（与现有行为一致）
- [ ] **FALL-03**: 降级事件写入 CI 日志，包含：使用的提供商、降级原因

### Documentation

- [ ] **DOCS-01**: 提供 `docs/ai-providers.md`，包含在 platform.openai.com 获取 OpenAI API Key 的操作步骤
- [ ] **DOCS-02**: 文档包含在 console.anthropic.com 获取 Anthropic API Key 的操作步骤
- [ ] **DOCS-03**: 文档说明如何在 GitHub Actions Repository Settings 中配置 `OPENAI_API_KEY` 和 `ANTHROPIC_API_KEY` Secrets
- [ ] **DOCS-04**: 文档说明 `AI_PROVIDER` 环境变量与 `plan/config.json` 的配置优先级规则

### Testing

- [ ] **TEST-01**: OpenAI 提供商路径有对应单元测试，API 调用通过 mock 隔离
- [ ] **TEST-02**: 降级逻辑有单元测试，覆盖主提供商失败 → 自动切换备用提供商的场景

## Future Requirements

### Content Quality (deferred from v1.1)

- **QUAL-01**: Topic tagging (science, health, education, etc.) in file header
- **QUAL-02**: Vocabulary reuse detection — skip words seen in previous N files
- **QUAL-03**: CEFR word-level annotation on vocabulary entries A2/B1/B2

### Operations

- **OPS-02**: Weekly digest: auto-generated `content/week-NN.md`

## Out of Scope

| Feature | Reason |
|---------|--------|
| Push notifications for content | Separate system; user reads from git directly |
| Interactive exercises / quiz UI | Static Markdown only; no web app |
| Multiple articles per day | One focused lesson beats information overload |
| Audio or video content | Text only |
| Grammar exercises | Chunking + comprehension sufficient for B1-B2 |
| User progress tracking | No state tracking for content consumption |
| Web scraping (non-RSS) | RSS-only keeps implementation stable and legal |
| Multi-provider load balancing | Overkill for one call/day; fallback is sufficient |

## Traceability

_Populated during roadmap creation._

| Requirement | Phase | Status |
|-------------|-------|--------|
| PRVD-01 | — | Pending |
| PRVD-02 | — | Pending |
| PRVD-03 | — | Pending |
| OAPI-01 | — | Pending |
| OAPI-02 | — | Pending |
| OAPI-03 | — | Pending |
| FALL-01 | — | Pending |
| FALL-02 | — | Pending |
| FALL-03 | — | Pending |
| DOCS-01 | — | Pending |
| DOCS-02 | — | Pending |
| DOCS-03 | — | Pending |
| DOCS-04 | — | Pending |
| TEST-01 | — | Pending |
| TEST-02 | — | Pending |

**Coverage:**
- v1.1 requirements: 15 total
- Mapped to phases: 0
- Unmapped: 15 ⚠️

---
*Requirements defined: 2026-03-23*
*Last updated: 2026-03-23 after v1.1 milestone start*
