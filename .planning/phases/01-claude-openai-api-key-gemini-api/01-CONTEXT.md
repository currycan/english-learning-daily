# Phase 1: Gemini Migration - Context

**Gathered:** 2026-03-24
**Status:** Ready for planning

<domain>
## Phase Boundary

删除 Claude（Anthropic SDK）和 OpenAI 的全部 API key 相关代码、配置字段、环境变量及 CI secrets，改用 Gemini API（`google-genai` SDK）作为唯一 AI provider。

Scope includes:
- `scripts/ai_provider.py` — 完全重写为 Gemini-only
- `scripts/generate_exercises.py` — 更新 `model_config` 结构
- `plan/config.json` — 替换 `ai_provider`/`openai_model`/`claude_model` 字段
- `.github/workflows/daily-content.yml` — 替换 env/secrets 注入
- `requirements.txt` — 删除 `anthropic`/`openai`，添加 `google-genai`
- `tests/test_ai_provider.py` + `tests/test_ai_provider_docs.py` — 重写为 Gemini 测试
- `docs/ai-providers.md` — 更新文档

</domain>

<decisions>
## Implementation Decisions

### Gemini SDK
- **D-01:** 使用 `google-genai`（新官方 SDK，`pip install google-genai`），不用旧版 `google-generativeai`。
  - Import: `from google import genai`
  - 客户端实例化在函数内部（符合现有模式，便于 mock 测试）：`client = genai.Client(api_key=key)`
  - 调用：`client.models.generate_content(model=..., contents=prompt)`
  - 返回文本：`response.text`

### Model
- **D-02:** 默认模型 `gemini-2.0-flash-lite`，成本最低，适合每天一次调用。
  - Config 字段：`gemini_model: "gemini-2.0-flash-lite"`（可覆盖）
  - 代码常量 `GEMINI_MODEL = "gemini-2.0-flash-lite"` 作为 fallback

### Fallback Strategy
- **D-03:** 完全删除 fallback 逻辑。移除 `_backup_provider()`、`_dispatch()`、`call_ai()` 的 retry 路径。
  - 替换为单一函数 `call_gemini(prompt, ...)` 返回文本，失败抛 `ProviderError`
  - `generate_exercises.py` 直接调用 `call_gemini()`，失败时 `sys.exit(1)`
  - 保留 `ProviderError` 异常类（语义清晰）

### Env Var & Config Naming
- **D-04:** 环境变量 `GEMINI_API_KEY`（不用 `GOOGLE_API_KEY`）
  - Priority: `os.environ.get("GEMINI_API_KEY") or config.get("gemini_api_key") or ""`
  - Config 字段：`gemini_model`（替换 `claude_model` / `openai_model`）
  - 删除的 config 字段：`ai_provider`, `openai_model`, `claude_model`, `anthropic_base_url`, `anthropic_auth_token`
  - 删除的 env vars：`ANTHROPIC_API_KEY`, `ANTHROPIC_BASE_URL`, `ANTHROPIC_AUTH_TOKEN`, `OPENAI_API_KEY`

### Claude's Discretion
- `google-genai` SDK 的确切 pip 版本号（选最新稳定版）
- docs/ai-providers.md 更新范围（保持双语格式，与现有风格一致）
- 测试 mock 策略（遵循现有 `call_gemini()` 函数内实例化客户端的模式）

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Current provider code (to be replaced)
- `scripts/ai_provider.py` — 当前 Claude/OpenAI 抽象层，了解要删除的代码结构
- `scripts/generate_exercises.py` — 当前调用方，了解 model_config 结构和 call_ai 用法

### Config & CI (to be updated)
- `plan/config.json` — 当前配置字段结构
- `.github/workflows/daily-content.yml` — 当前 CI env/secrets 注入方式

### Dependencies (to be modified)
- `requirements.txt` — 当前依赖列表

### Tests (to be rewritten)
- `tests/test_ai_provider.py` — 当前 AI provider 单元测试
- `tests/test_ai_provider_docs.py` — 当前文档测试

### Project guidelines
- `CLAUDE.md` — Project-specific constraints (immutability, no secrets in code, sys.exit on error)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `ProviderError` exception class — 保留，语义清晰
- `resolve_provider()` 函数模式 — 简化为 `resolve_api_key()` 或直接在 `call_gemini()` 内处理
- `_load_config()` in `generate_exercises.py` — 无需修改

### Established Patterns
- SDK 客户端在函数内部实例化（`genai.Client()` inside `call_gemini()`）— 保持一致
- `ProviderError` 在底层抛出，`generate_exercises.py` 捕获并 `sys.exit(1)`
- 错误信息打印到 `sys.stderr`，INFO/WARNING/ERROR 前缀

### Integration Points
- `generate_exercises.py:main()` — 当前调用 `resolve_provider()` + `call_ai()`，改为直接调用 `call_gemini()`
- `daily-content.yml` generate step — 删除 4 个旧 secrets，添加 `GEMINI_API_KEY`

</code_context>

<specifics>
## Specific Ideas

- `call_gemini()` 函数签名建议：`call_gemini(prompt: str, max_tokens: int = 2048, model: str | None = None, api_key: str | None = None) -> str`
- `generate_exercises.py` 的 `model_config` dict 简化为只有 `gemini_model` 字段

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 01-claude-openai-api-key-gemini-api*
*Context gathered: 2026-03-24*
