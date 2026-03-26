# Script Reference / 脚本参考手册

> English · 中文对照

---

## Content Generation Scripts / 内容生成脚本

### `scripts/content_utils.py`

Shared utilities for the content generation pipeline.

内容生成流水线的共用工具。

**Exports / 导出：**

| Symbol / 符号 | Type / 类型 | Description / 说明 |
|---------------|-------------|-------------------|
| `BEIJING_TZ` | `timezone` | UTC+8 timezone constant / UTC+8 时区常量 |
| `CONTENT_DIR` | `Path` | `Path("content")` — output directory / 输出目录 |
| `get_beijing_date()` | `() → date` | Today's date in CST (UTC+8) / 北京时间今日日期 |
| `content_path(d)` | `(date) → Path` | `content/YYYY-MM-DD.md` for a given date / 给定日期的内容文件路径 |

**Why `get_beijing_date()` not `date.today()` / 为什么不用 `date.today()`：**

GitHub Actions runners use UTC. Calling `date.today()` at 22:30 UTC returns today's UTC date, but it is already tomorrow in Beijing (06:30 BJT). `datetime.now(tz=BEIJING_TZ).date()` always returns the correct Beijing date.

GitHub Actions 服务器使用 UTC。在 UTC 22:30 调用 `date.today()` 返回 UTC 今天，但北京时间已是明天（06:30 BJT）。`datetime.now(tz=BEIJING_TZ).date()` 始终返回正确的北京日期。

---

### `scripts/feed_article.py`

Fetches one English article from RSS and outputs an Article Envelope JSON to stdout.

从 RSS 源抓取一篇英语文章，将文章信封 JSON 输出到 stdout。

**Usage / 用法：**

```bash
python -m scripts.feed_article
# Outputs to stdout (JSON)
# 输出到 stdout（JSON）
```

**Output format / 输出格式：**

```json
{
  "title": "Article Title",
  "body": "Full article text (plain text, HTML stripped)...",
  "source_url": "https://example.com/article"
}
```

**Behavior / 行为：**

1. If today's content file already exists → `exit 0` (idempotency guard)
2. Fetch primary RSS feed (`newsinlevels.com/feed`)
3. Select best entry by topic keywords
4. Validate: title + body ≥ 200 chars + source URL all present
5. If primary fails → try fallback feed (BBC Learning English)
6. If both fail → print error to stderr + `exit 1`

1. 若今天的内容文件已存在 → `exit 0`（幂等守卫）
2. 抓取主 RSS 源（`newsinlevels.com/feed`）
3. 按话题关键词选择最佳条目
4. 验证：标题 + 正文 ≥ 200 字符 + 来源 URL 均存在
5. 主源失败 → 尝试备用源（BBC Learning English）
6. 两者均失败 → 向 stderr 输出错误 + `exit 1`

**Key functions / 关键函数：**

| Function / 函数 | Description / 说明 |
|-----------------|-------------------|
| `clean_html(raw)` | Strip HTML tags, decode entities, collapse whitespace / 清除 HTML 标签、解码实体、压缩空白 |
| `_validate(envelope)` | Check title, body ≥ 200 chars, source_url present / 验证标题、正文 ≥ 200 字符、来源 URL 存在 |
| `fetch_article(config)` | Primary + fallback cascade, exits 1 on total failure / 主源 + 备用源级联，全部失败时 exit 1 |
| `main()` | Entry point: idempotency check + fetch + JSON print / 入口：幂等检查 + 抓取 + 输出 JSON |

---

### `scripts/generate_exercises.py`

Reads an Article Envelope JSON from stdin, calls the Claude API once, outputs a complete Markdown lesson to stdout.

从 stdin 读取文章信封 JSON，调用一次 Claude API，将完整 Markdown 课程输出到 stdout。

**Usage / 用法：**

```bash
# Standalone (reads JSON from stdin)
echo '{"title":"...", "body":"...", "source_url":"..."}' | python -m scripts.generate_exercises

# In pipeline (typical usage)
python -m scripts.feed_article | python -m scripts.generate_exercises
```

**Requires / 需要：** `ANTHROPIC_API_KEY` environment variable.

需要 `ANTHROPIC_API_KEY` 环境变量。

**Output format / 输出格式：**

A four-section Markdown lesson file:

四段式 Markdown 课程文件：

```markdown
## 📖 文章 / Article
[full article text]
> Source: [url]

## 📚 词汇 / Vocabulary
**word** (part_of_speech) （中文释义）— English definition
> "verbatim example from article"

## 🔗 表达 / Chunking Expressions
**phrase** （中文释义）
English usage explanation
- Generated example 1
- Generated example 2

## ❓ 理解 / Comprehension
**Q: Question?**
**A (EN):** English answer
**A (中):** Chinese answer
```

**Claude API call spec / Claude API 调用规范：**

| Parameter / 参数 | Value / 值 |
|------------------|------------|
| Model / 模型 | `claude-3-5-haiku-20241022` |
| Max tokens / 最大 token 数 | 2048 |
| Calls per day / 每日调用次数 | 1 |
| Estimated tokens / 估计 token 数 | ~1,400/day |

**Key functions / 关键函数：**

| Function / 函数 | Description / 说明 |
|-----------------|-------------------|
| `build_prompt(envelope)` | Constructs structured JSON-instruction prompt / 构建结构化 JSON 指令 prompt |
| `call_claude(prompt)` | Calls API, exits 1 on any error / 调用 API，任何错误均 exit 1 |
| `parse_response(raw_text)` | Validates JSON structure and counts / 验证 JSON 结构和数量 |
| `render_markdown(envelope, exercises)` | Renders the four-section Markdown / 渲染四段式 Markdown |

---

### `scripts/commit_content.py`

Reads Markdown from stdin, writes to `content/YYYY-MM-DD.md`, and commits + pushes to git.

从 stdin 读取 Markdown，写入 `content/YYYY-MM-DD.md`，提交并推送到 git。

**Usage / 用法：**

```bash
# In full pipeline
python -m scripts.feed_article | \
python -m scripts.generate_exercises | \
python -m scripts.commit_content
```

**Behavior / 行为：**

1. Get today's Beijing date
2. If `content/YYYY-MM-DD.md` exists → `exit 0` (idempotency)
3. Read Markdown from stdin
4. If stdin is empty → `exit 1`
5. Write file to `content/` directory (creates directory if needed)
6. `git add` → `git commit -m "content: add YYYY-MM-DD"` → `git push`
7. Any git error → `exit 1`

1. 获取北京时间今日日期
2. 若 `content/YYYY-MM-DD.md` 已存在 → `exit 0`（幂等）
3. 从 stdin 读取 Markdown
4. 若 stdin 为空 → `exit 1`
5. 写入文件到 `content/` 目录（按需创建目录）
6. `git add` → `git commit -m "content: add YYYY-MM-DD"` → `git push`
7. 任何 git 错误 → `exit 1`

**CI requirements / CI 需要：**

The workflow must configure git identity before this step:

工作流必须在此步骤前配置 git 身份：

```yaml
- name: Configure git identity
  run: |
    git config user.name "github-actions[bot]"
    git config user.email "github-actions[bot]@users.noreply.github.com"
```

And the job must have write permissions:

且 job 必须有写权限：

```yaml
permissions:
  contents: write
```

---

## Push Notification Scripts / 推送通知脚本

### `scripts/plan_state.py`

All temporal calculations and `state.json` I/O for the push notification system.

推送通知系统的所有时间计算和 `state.json` 读写。

**Key rule / 核心规则：** All temporal values (`current_week`, `plan_day`, `scene_cycle_day`, etc.) are **derived** from `start_date` at runtime. They are **never stored** in `state.json`.

所有时间值（当前周次、计划天数、场景周期天数等）均在运行时从 `start_date` **推算**。它们**绝不存储**在 `state.json` 中。

---

### `scripts/generate_task.py`

Builds the morning push notification payload.

构建早间推送通知内容。

**Usage / 用法：**

```bash
python -m scripts.generate_task
# Outputs: {"title": "...", "body": "...", "url": null}
```

---

### `scripts/check_evening.py`

Builds the evening push notification payload (completion summary + tomorrow preview).

构建晚间推送通知内容（完成情况汇总 + 明日预告）。

**Usage / 用法：**

```bash
python -m scripts.check_evening
# Outputs: {"title": "...", "body": "...", "url": null}
```

---

### `scripts/push_bark.py`

Bark API client. Reads a JSON envelope from stdin and sends a push notification to iPhone.

Bark API 客户端。从 stdin 读取 JSON 信封，向 iPhone 发送推送通知。

**Usage / 用法：**

```bash
python -m scripts.generate_task | python -m scripts.push_bark
```

**Requires / 需要：** `BARK_TOKEN` environment variable (set as GitHub Secret).

需要 `BARK_TOKEN` 环境变量（在 GitHub Secret 中设置）。

