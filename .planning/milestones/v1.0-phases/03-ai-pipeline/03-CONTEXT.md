# Phase 3: AI Pipeline - Context

**Gathered:** 2026-03-23
**Status:** Ready for planning

<domain>
## Phase Boundary

从 `feed_article.py`（Phase 2）的 stdout Article Envelope JSON 出发，调用 Claude API 生成词汇、chunking 表达和阅读理解题，将文章正文 + AI 生成内容渲染为 `content/YYYY-MM-DD.md`，并 git commit + push。Phase 3 完成后，完整 pipeline 可端到端运行。

不涉及：RSS 获取（Phase 2 已完成）、push 通知、用户进度跟踪。

</domain>

<decisions>
## Implementation Decisions

### 脚本架构（Pipeline Wiring）
- 新建 `scripts/generate_exercises.py`：从 stdin 读取 Article Envelope JSON，调用 Claude API，将 Markdown 内容输出到 stdout
- 更新 `scripts/commit_content.py`（替换 Phase 1 占位实现）：从 stdin 读取完整 Markdown 内容，写入 `content/YYYY-MM-DD.md`，执行 git add + commit + push
- Workflow 最终形态：`python -m scripts.feed_article | python -m scripts.generate_exercises | python -m scripts.commit_content`
- 管道中任何一步失败 → 后续步骤不执行 → CI job 标记 failed（exit 非零）

### Claude API 调用
- **调用次数**：一次 API 调用（STATE.md 已决策：每天一次，单次结构化 JSON prompt）
- **输出格式**：结构化 JSON（不是直接输出 Markdown），便于程序解析后精确渲染
- **模型**：`claude-3-5-haiku-20241022`（已在 STATE.md 锁定）
- **JSON schema**：
  ```json
  {
    "vocabulary": [
      {
        "word": "...",
        "part_of_speech": "...",
        "chinese_meaning": "...",
        "definition": "...",
        "example": "..."
      }
    ],
    "chunks": [
      {
        "chunk": "...",
        "chinese_meaning": "...",
        "english_explanation": "...",
        "examples": ["...", "..."]
      }
    ],
    "questions": [
      {
        "question": "...",
        "answer_en": "...",
        "answer_zh": "..."
      }
    ]
  }
  ```
- **Claude 指令要求**：
  - 词汇定义必须用 B1-B2 简单英语写（不能用比目标词更难的词来解释）
  - 例句必须来自原文（直接引用，不是生成）
  - Chunk 例句可以是生成的（展示用法变化），但须自然地道
  - 阅读理解至少包含一道推断题（非纯事实回忆）

### Markdown 文件结构
- **整体布局**：单文件，四个 section 顺序排列（全部合一，非早晚分割）
- **Section 标题**：中英双语，带 emoji，例如：
  - `## 📖 文章 / Article`
  - `## 📚 词汇 / Vocabulary`
  - `## 🔗 表达 / Chunking Expressions`
  - `## ❓ 理解 / Comprehension`
- **文章正文**：原文直接输出，段落保留，最后一行加来源：`> Source: [URL]`

### 词汇条目格式
每个词汇条目格式：
```
**word** (part_of_speech) （中文释义）— Plain English definition.
> "Original example sentence from the article."
```
- 词 + 词性 + 中文释义 + 简单英语定义 + 原文例句
- 5–8 个词（由 Claude 从文章中选取 B1-B2 级别关键词）

### Chunking 表达格式
每个 chunk 条目格式：
```
**chunk expression** （中文含义）
English explanation of usage context and register.
- Example sentence one showing the chunk in use.
- Example sentence two showing variation or different context.
```
- Chunk + 中文含义 + 英文用法说明 + 2 个例句
- 3–5 个 chunk（Claude 从文章中提取自然英语短语和搭配）

### 阅读理解题格式
每道题格式：
```
**Q: Question in English?**
**A (EN):** English answer.
**A (中):** 中文要点说明。
```
- 问题用英文，答案中英双语
- 3–5 道题，至少 1 道推断题
- 题目和答案均由 Claude 生成

### 输出语言总则
- **中文输出**：词汇中文释义、chunk 中文含义、答案中文说明 → 全部用中文
- **英文保留**：文章原文、词汇英文定义、chunk 英文说明、例句、理解题题干 → 保持英文
- **双语答案**：理解题答案同时提供英文和中文两个版本

### Claude's Discretion
- `generate_exercises.py` 内部的 prompt 具体措辞（只要满足上述要求）
- Claude API 的 `max_tokens` 和 `temperature` 参数
- 错误时的重试次数（STATE.md 提到验证 SDK 版本，具体实现由 planner 决定）
- `generate_exercises.py` 的函数拆分方式（如 `build_prompt()`, `parse_response()`, `render_markdown()` 等）

</decisions>

<canonical_refs>
## Canonical References

**下游 Agent 执行前必须阅读这些文件。**

### 项目需求与约束
- `.planning/REQUIREMENTS.md` §AI Generation (AIGEN-01~04) 和 §Output (OUT-01~03) — 验收标准
- `.planning/PROJECT.md` — 技术栈约束（Python only，`anthropic` SDK，无 secrets 入代码，ANTHROPIC_API_KEY 来自 GitHub Secrets）

### 现有代码（必须阅读后再实现）
- `scripts/feed_article.py` — Phase 2 输出的 Article Envelope JSON 结构（`title`, `body`, `source_url`）；`generate_exercises.py` 从 stdin 读取此格式
- `scripts/commit_content.py` — Phase 1 占位实现，Phase 3 需要替换其 `main()` 逻辑（从 stdin 读 Markdown，写文件，git commit）
- `scripts/content_utils.py` — `get_beijing_date()`, `content_path()`, `CONTENT_DIR` — commit_content.py 继续使用
- `scripts/push_bark.py` — stdin 读取 + `sys.exit(1)` 错误处理的参考实现

### CI Workflow
- `.github/workflows/daily-content.yml` — Phase 3 需将 workflow 的运行步骤从占位脚本更新为完整 pipeline

### 已有决策记录
- `.planning/STATE.md` §Accumulated Context — 包含已锁定的 `feedparser`、`claude-3-5-haiku-20241022`、每天一次 API 调用等关键决策

</canonical_refs>

<code_context>
## Existing Code Insights

### 可复用资产
- `scripts/content_utils.py`：`get_beijing_date()` + `content_path()` + `CONTENT_DIR` — commit_content.py 继续调用，无需修改
- `scripts/commit_content.py`：`git_commit_and_push(path, today)` 函数已实现，Phase 3 只需替换 `main()` 逻辑（从写占位文本改为从 stdin 读 Markdown 内容）
- `scripts/push_bark.py`：stdin JSON 读取模式（`json.load(sys.stdin)`）可作为 generate_exercises.py 读取 Article Envelope 的参考
- `requirements.txt`：`anthropic` SDK 已在依赖列表（或需确认并添加）

### 已确立模式
- `sys.exit(1)` + `print(..., file=sys.stderr)`：所有错误路径
- 纯函数 + 类型注解：`def build_prompt(article: dict) -> str:`
- `main()` 入口：所有可执行脚本
- stdout JSON / Markdown 输出：管道中间节点输出到 stdout，最后节点写文件

### 集成点
- `generate_exercises.py` stdin ← `feed_article.py` stdout（Article Envelope JSON）
- `generate_exercises.py` stdout → `commit_content.py` stdin（完整 Markdown 字符串）
- `daily-content.yml` workflow：Phase 3 完成后替换单行占位命令为三段管道命令

</code_context>

<specifics>
## Specific Ideas

- 用户早晨阅读「文章 + 词汇」，晚上回顾「表达 + 理解题」——虽然文件合一，section 顺序的安排（先文章词汇，后 chunk 和理解）天然支持这种分段阅读习惯
- 内容为中文母语学习者设计：中文释义是核心辅助，不是可选项
- STATE.md 警告：实现前需验证 `anthropic` SDK 当前 PyPI 版本，并确认 `claude-3-5-haiku-20241022` model ID 仍有效

</specifics>

<deferred>
## Deferred Ideas

- 词汇去重检测（避免本周已学的词再次出现）— v2 QUAL-02
- CEFR 词汇级别标注（A2/B1/B2）— v2 QUAL-03
- 话题标签自动分类 — v2 QUAL-01
- 每周词汇汇总 — v2 OPS-02

</deferred>

---

*Phase: 03-ai-pipeline*
*Context gathered: 2026-03-23*
