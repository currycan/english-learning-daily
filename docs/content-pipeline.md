# Daily Content Pipeline / 每日内容生成流水线

> English · 中文对照 — Deep-dive technical reference

---

## What It Does / 它做什么

Every day at 06:00 BJT, GitHub Actions runs a three-stage pipeline that:

每天北京时间 06:00，GitHub Actions 运行一个三阶段流水线：

1. **Fetches** a real English news article from an RSS feed
2. **Generates** AI-powered exercises (vocabulary + chunking expressions + comprehension Q&A)
3. **Commits** the combined lesson to `content/YYYY-MM-DD.md`

1. 从 RSS 源**抓取**一篇真实英语新闻文章
2. **生成** AI 练习（词汇 + 表达块 + 理解问答）
3. 将合并后的课程**提交**到 `content/YYYY-MM-DD.md`

The result is a growing git library of ready-to-read English lessons, one per day.

结果是一个不断增长的 git 库，每天一篇即可阅读的英语课程。

---

## Pipeline Stages / 流水线阶段

### Stage 1: `feed_article.py` — Article Fetch / 文章抓取

**Input / 输入：** No stdin input (reads `plan/config.json` for feed URLs)

无 stdin 输入（从 `plan/config.json` 读取 RSS 源 URL）

**Output / 输出：** Article Envelope JSON on stdout

Article Envelope JSON 输出到 stdout

```json
{
  "title": "Scientists Discover New Planet",
  "body": "A team of researchers announced today that they have found...",
  "source_url": "https://www.newsinlevels.com/products/..."
}
```

**Selection logic / 选择逻辑：**

```
1. Fetch primary RSS feed
2. For each entry (up to 3 attempts):
   - Prefer entries whose title+summary contains a topic keyword
   - Extract body from content:encoded > summary > description
   - Strip HTML tags (HTMLParser, not regex)
   - Validate: title ✓, body ≥ 200 chars ✓, source_url ✓
   - If valid → output and exit
3. If primary fails → repeat with fallback feed
4. If fallback fails → exit 1
```

**HTML cleaning approach / HTML 清理方法：**

Uses a `HTMLParser` subclass (`_TextExtractor`) rather than regex. This correctly handles:
- Nested HTML tags
- HTML entities (`&amp;`, `&nbsp;`, etc.)
- Block tags → newlines (`<p>`, `<br>`, `<li>`, etc.)

使用 `HTMLParser` 子类（`_TextExtractor`）而非正则表达式。这能正确处理：
- 嵌套 HTML 标签
- HTML 实体（`&amp;`、`&nbsp;` 等）
- 块级标签 → 换行（`<p>`、`<br>`、`<li>` 等）

---

### Stage 2: `generate_exercises.py` — AI Exercise Generation / AI 练习生成

**Input / 输入：** Article Envelope JSON on stdin

stdin 接收 Article Envelope JSON

**Output / 输出：** Full Markdown lesson on stdout

完整 Markdown 课程输出到 stdout

**Prompt structure / Prompt 结构：**

The prompt instructs Claude to return a single JSON object with three arrays:

Prompt 指示 Claude 返回包含三个数组的 JSON 对象：

```
vocabulary (5–8 items):
  - word, part_of_speech, chinese_meaning
  - definition (plain English, B1-B2 level)
  - example (verbatim quote from article)

chunks (3–5 items):
  - chunk (natural phrase/collocation from article)
  - chinese_meaning
  - english_explanation (usage context and register)
  - examples (2 generated sentences in varied contexts)

questions (3–5 items):
  - question (in English)
  - answer_en
  - answer_zh
  - ≥1 must be inferential (not just factual recall)
```

**Response validation / 响应验证：**

After the API call, `parse_response()` checks:

API 调用后，`parse_response()` 检查：

- Response is valid JSON
- All three keys present (`vocabulary`, `chunks`, `questions`)
- `vocabulary` has ≥ 5 items
- Handles accidental code fences from Claude (defensive strip)

- 响应是有效 JSON
- 三个键均存在（`vocabulary`、`chunks`、`questions`）
- `vocabulary` 至少有 5 个条目
- 处理 Claude 意外输出的代码围栏（防御性清除）

**Markdown rendering / Markdown 渲染：**

`render_markdown()` produces this four-section structure:

`render_markdown()` 生成以下四段结构：

```markdown
## 📖 文章 / Article
[article body]
> Source: [url]

## 📚 词汇 / Vocabulary
**word** (pos) （中文）— definition
> "verbatim example"

## 🔗 表达 / Chunking Expressions
**phrase** （中文）
English usage explanation
- Example sentence 1
- Example sentence 2

## ❓ 理解 / Comprehension
**Q: Question?**
**A (EN):** English answer
**A (中):** Chinese answer
```

---

### Stage 3: `commit_content.py` — Git Commit / Git 提交

**Input / 输入：** Markdown text on stdin

stdin 接收 Markdown 文本

**Output / 输出：** `content/YYYY-MM-DD.md` committed and pushed to git

`content/YYYY-MM-DD.md` 提交并推送到 git

**Commit message / 提交信息：** `content: add YYYY-MM-DD`

**Idempotency check / 幂等检查：** Checks for file existence before writing. Safe to re-run.

写入前检查文件是否存在。可安全重复运行。

---

## Failure Modes / 故障模式

| Failure / 故障 | Stage / 阶段 | Behavior / 行为 |
|----------------|-------------|----------------|
| RSS primary unreachable | Stage 1 | Try fallback feed / 尝试备用源 |
| Both feeds unreachable | Stage 1 | `exit 1` → CI job fails / CI 任务失败 |
| No valid article in feeds | Stage 1 | `exit 1` → CI job fails / CI 任务失败 |
| Claude API error | Stage 2 | `exit 1` → CI job fails, no partial file / CI 任务失败，无残缺文件 |
| Claude returns malformed JSON | Stage 2 | `exit 1` → CI job fails / CI 任务失败 |
| Claude returns < 5 vocabulary | Stage 2 | `exit 1` → CI job fails / CI 任务失败 |
| Empty stdin to commit_content | Stage 3 | `exit 1` → CI job fails / CI 任务失败 |
| File already exists (today) | Stage 1 or 3 | `exit 0` — idempotent, no duplicate / 幂等，不重复 |
| Git push fails | Stage 3 | `exit 1` → CI job fails / CI 任务失败 |

`set -eo pipefail` ensures any `exit 1` in any stage fails the entire pipeline step.

`set -eo pipefail` 确保任意阶段的 `exit 1` 都会导致整个流水线步骤失败。

---

## Cost Analysis / 成本分析

| Item / 项目 | Value / 值 |
|-------------|-----------|
| Model / 模型 | `claude-3-5-haiku-20241022` |
| API calls / 每日调用次数 | 1 call/day |
| Estimated input tokens / 估计输入 token | ~800 (article + prompt) |
| Estimated output tokens / 估计输出 token | ~600 (exercises JSON) |
| Total tokens/day / 每日总 token | ~1,400 |
| Approx cost/day (Haiku pricing) / 约每日费用 | < $0.01 |
| Approx cost/month / 约每月费用 | < $0.30 |

---

## Extending the Pipeline / 扩展流水线

### Add a new RSS source / 添加新 RSS 源

Edit `plan/config.json`:

编辑 `plan/config.json`：

```json
{
  "content_feeds": {
    "primary_url": "https://your-new-feed.com/rss",
    "fallback_url": "https://existing-fallback.com/rss",
    "content_topics": ["your", "topic", "keywords"]
  }
}
```

Verify the feed returns 200+ character body text before committing.

提交前验证该源能返回 200 字符以上的正文。

### Modify exercise format / 修改练习格式

1. Edit the prompt in `build_prompt()` in `generate_exercises.py`
2. Update `render_markdown()` to match new JSON structure
3. Update `parse_response()` validation if new required keys added
4. Update `tests/test_generate_exercises.py` to reflect changes

1. 编辑 `generate_exercises.py` 中 `build_prompt()` 的 prompt
2. 更新 `render_markdown()` 以匹配新 JSON 结构
3. 若新增必需键，更新 `parse_response()` 的验证逻辑
4. 更新 `tests/test_generate_exercises.py` 以反映变更

### Change the AI model / 更换 AI 模型

Edit `MODEL` constant in `generate_exercises.py`:

编辑 `generate_exercises.py` 中的 `MODEL` 常量：

```python
MODEL = "claude-3-5-haiku-20241022"  # current / 当前
# MODEL = "claude-3-5-sonnet-20241022"  # higher quality, higher cost
```

Update `tests/test_generate_exercises.py` mock if model name changes.

若模型名变更，相应更新 `tests/test_generate_exercises.py` 中的 mock。
