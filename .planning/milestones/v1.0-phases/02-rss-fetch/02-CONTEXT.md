# Phase 2: RSS Fetch - Context

**Gathered:** 2026-03-23
**Status:** Ready for planning

<domain>
## Phase Boundary

从 VOA Special English RSS 获取每日一篇英语文章（BBC 为备用），验证文章有效性，并将结构化的 Article Envelope JSON 输出到 stdout，供 Phase 3 AI 生成环节消费。

本阶段不涉及 AI 调用、Markdown 渲染或 git 提交——仅负责获取与校验。

</domain>

<decisions>
## Implementation Decisions

### 文章选取策略
- **关键词过滤优先**：遍历当天 RSS feed 条目，优先选取 title 或 summary 中包含 `content_topics` 关键词的最新一篇
- **无匹配兜底**：当天没有条目匹配关键词时，退回取 feed 中最新一篇（保证每天都有内容产出，而非空白）
- **话题偏好**：用户关注国际大事、日常交流类新闻，重点关注 AI / 科技资讯
- **初始关键词列表**：`["AI", "artificial intelligence", "technology", "international", "economy", "science", "climate"]`——存在 `plan/config.json` 的 `content_topics` 字段，无需改代码即可调整

### 正文清理规则
- **工具**：Python 标准库 `html.parser`——不增加任何新依赖
- **目标格式**：纯文本 + 段落换行（段落间保留一个空行），所有 HTML 标签去除
- **交付给 Phase 3**：可读的自然英语正文，AI 可直接用于提取词汇和生成问题

### Feed URL 配置方式
- **存储位置**：现有 `plan/config.json`，新增 `content_feeds` 字段（不新建配置文件）
- **字段结构**：
  ```json
  "content_feeds": {
    "primary_url": "https://feeds.voanews.com/learningenglish/english",
    "fallback_url": "https://www.bbc.co.uk/learningenglish/english/features/lingohack/feed.rss",
    "content_topics": ["AI", "artificial intelligence", "technology", "international", "economy", "science", "climate"]
  }
  ```
- **RSS 解析库**：`feedparser`——加入 `requirements.txt`（STATE.md 已决策：feedparser 处理不规范 XML/CDATA 比 xml.etree 更健壮）

### 文章有效性验证
- **三个硬指标**（全部满足才算有效）：
  1. `title` 非空（非空字符串）
  2. `body`（清理后）≥ 200 字符
  3. `source_url` 非空（非空字符串）
- **失败处理**：当前条目验证失败，顺序尝试 feed 中下一篇，最多尝试 3 篇；3 篇全失败则切换备用 feed（BBC）；BBC 也失败则 `sys.exit(1)` + 清晰错误信息到 stderr

### Article Envelope JSON 输出格式
- **输出方式**：stdout JSON（与现有 push_bark.py 的 stdin 消费模式一致）
- **字段**：
  ```json
  {
    "title": "...",
    "body": "...",
    "source_url": "..."
  }
  ```
- Phase 3 的 `generate_exercises.py` 从 stdin 读取此 JSON（管道模式）

### Claude's Discretion
- `feedparser` 的具体版本号
- 从 `feedparser` entry 提取 body 的字段优先级（`content[0].value` > `summary` > `description`）
- 正文清理时多余空白的标准化规则（如连续多个空行压缩为一个）

</decisions>

<canonical_refs>
## Canonical References

**下游 Agent 执行前必须阅读这些文件。**

### 项目约束与需求
- `.planning/REQUIREMENTS.md` §Fetch — FTCH-01、FTCH-02、FTCH-03 验收标准
- `.planning/PROJECT.md` — 技术栈约束（Python only，依赖最小化，无 secrets 入代码）

### 现有代码模式（必须遵循）
- `scripts/push_bark.py` — stdout→stdin JSON 管道模式的参考实现；`requests` 的用法和错误处理模式
- `scripts/content_utils.py` — 北京时区日期推导；`content_path()` 用于幂等检查
- `scripts/commit_content.py` — Phase 1 占位脚本，Phase 2 不修改它，但 fetch 输出最终会由它的后继脚本消费

### 配置文件（读取并扩展）
- `plan/config.json` — 现有配置结构；Phase 2 新增 `content_feeds` 字段

### CI 模式
- `.github/workflows/daily-content.yml` — Phase 1 创建的工作流；Phase 2 不修改它，但 fetch 脚本将在其中运行

</canonical_refs>

<code_context>
## Existing Code Insights

### 可复用资产
- `scripts/push_bark.py`：`requests.post(..., timeout=10)` + HTTP 状态码检查 + `sys.exit(1)` 模式——fetch 脚本的 HTTP 错误处理应完全遵循此模式
- `scripts/content_utils.py`：`get_beijing_date()` + `content_path()`——fetch 脚本调用 `content_path(get_beijing_date())` 做幂等检查（文件已存在则 `sys.exit(0)`）
- `plan/config.json`：已有配置文件，直接扩展 `content_feeds` 字段

### 已确立模式
- `sys.exit(1)` + `print(..., file=sys.stderr)`：所有错误路径必须遵循
- 纯函数 + 类型注解：`def fetch_article(config: dict) -> dict:` 风格
- `main()` 入口：所有可执行脚本统一模式
- stdout JSON 输出：`json.dumps(envelope)` + `print()` 到 stdout
- `requests` 已在 `requirements.txt`（2.32.3）——无需重复安装

### 集成点
- `fetch_article.py` 输出 → `generate_exercises.py` stdin（Phase 3）
- `daily-content.yml` 工作流：Phase 2 完成后，workflow 步骤将从 `python -m scripts.commit_content`（占位）变为 `python -m scripts.fetch_article | python -m scripts.generate_exercises | python -m scripts.commit_content`（Phase 3 完成后）

</code_context>

<specifics>
## Specific Ideas

- 用户早晨（08:30 工作日，09:30 周末）阅读，内容需在 06:00 BJT（22:00 UTC cron）前准备好
- 话题偏好：国际大事 + 日常交流 + AI/科技资讯——关键词列表应覆盖这三类
- VOA Special English 已针对 B1-B2 学习者设计，无需额外难度过滤

</specifics>

<deferred>
## Deferred Ideas

- 话题标签自动分类（归入 v2 QUAL-01）——Phase 2 只做关键词过滤，不做标签
- 词汇去重检测（QUAL-02）——Phase 3 之后的事
- 已读文章去重（避免重复抓同一篇）——v2 需求，Phase 2 不实现

</deferred>

---

*Phase: 02-rss-fetch*
*Context gathered: 2026-03-23*
