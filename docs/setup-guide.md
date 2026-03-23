# Setup Guide / 部署指南

> English · 中文对照

---

## Prerequisites / 前置条件

| Requirement / 要求 | Details / 说明 |
|--------------------|----------------|
| GitHub account | Free tier sufficient / 免费账号即可 |
| iPhone with Bark app | Download from App Store / 从 App Store 下载 |
| Anthropic API key | Required for content generation / 内容生成必需 |
| Python 3.12+ | For local development only / 仅本地开发需要 |

---

## Part 1: Push Notification System / 第一部分：推送通知系统

### Step 1 — Fork the repository / 第一步：Fork 仓库

Click **Fork** on GitHub to create your own copy.

点击 GitHub 上的 **Fork** 创建你自己的副本。

### Step 2 — Get your Bark Token / 第二步：获取 Bark Token

1. Install [Bark](https://bark.day.app/) on your iPhone.
2. Open the app — your token is shown on the home screen.
3. Copy only the **token** (the path segment after the server URL, e.g. `AbCdEfGhIjKlMnOp`).

在 iPhone 上安装 [Bark](https://bark.day.app/)。
打开 App — 首页即显示你的 token。
只复制 **token**（服务器 URL 后面的路径段，如 `AbCdEfGhIjKlMnOp`）。

### Step 3 — Add BARK_TOKEN secret / 第三步：添加 BARK_TOKEN Secret

In your GitHub repository:

在 GitHub 仓库中：

```
Settings → Secrets and variables → Actions → New repository secret
  Name:  BARK_TOKEN
  Value: <your token>
```

### Step 4 — Set your start date / 第四步：设置开始日期

Edit `plan/state.json`:

编辑 `plan/state.json`：

```json
{
  "start_date": "2026-03-21",
  "scene_ratings": {},
  "daily_log": {}
}
```

Set `start_date` to the date you want Week 1 to begin (YYYY-MM-DD format).

将 `start_date` 设为你希望第一周开始的日期（YYYY-MM-DD 格式）。

### Step 5 — Enable GitHub Actions / 第五步：启用 GitHub Actions

```
Settings → Actions → General → Allow all actions and reusable workflows
```

Actions will then trigger automatically at 07:00 and 21:00 BJT every day.

之后每天 07:00 和 21:00（北京时间）自动触发，无需手动操作。

---

## Part 2: Content Generation System / 第二部分：内容生成系统

### Step 6 — Get an Anthropic API Key / 第六步：获取 Anthropic API Key

Sign up at [console.anthropic.com](https://console.anthropic.com) and create an API key.

在 [console.anthropic.com](https://console.anthropic.com) 注册并创建 API key。

**Cost estimate / 费用估算：** ~1,400 tokens per day using `claude-3-5-haiku-20241022`. At current Haiku pricing this is under $0.01/day.

使用 `claude-3-5-haiku-20241022` 每天约消耗 1,400 tokens。按当前 Haiku 定价低于 $0.01/天。

### Step 7 — Add ANTHROPIC_API_KEY secret / 第七步：添加 ANTHROPIC_API_KEY Secret

```
Settings → Secrets and variables → Actions → New repository secret
  Name:  ANTHROPIC_API_KEY
  Value: <your Anthropic API key>
```

The key is injected into the CI environment — it is **never** stored in code.

该 key 注入到 CI 环境中——**绝不**存储在代码中。

### Step 7a — For OpenAI + dual-provider setup / 第 7a 步：OpenAI 双提供商配置（可选）

For dual-provider setup (OpenAI + Anthropic with automatic fallback), see [`docs/ai-providers.md`](./ai-providers.md).

如需配置 OpenAI + Anthropic 双提供商（含自动降级），请参阅 [`docs/ai-providers.md`](./ai-providers.md)。

### Step 8 — Verify content feed URLs (optional) / 第八步：验证内容源 URL（可选）

The default RSS feeds are configured in `plan/config.json`:

默认 RSS 源配置在 `plan/config.json` 中：

```json
{
  "content_feeds": {
    "primary_url": "https://www.newsinlevels.com/feed",
    "fallback_url": "https://www.bbc.co.uk/learningenglish/english/features/lingohack/feed.rss",
    "content_topics": ["AI", "technology", "international", "economy", "science", "climate"]
  }
}
```

`primary_url` — fetched first. Must return articles with 200+ character body text.

`fallback_url` — used if primary fails.

`content_topics` — keyword list for article selection (prefers articles matching these topics).

`primary_url` — 优先抓取。要求正文至少 200 字符。
`fallback_url` — 主源失败时使用。
`content_topics` — 文章选择关键词列表（优先选择包含这些话题的文章）。

---

## Manual Testing / 手动测试

### Test push notifications locally / 本地测试推送通知

```bash
# Install dependencies
pip install -r requirements.txt

# Preview morning push payload (no network call)
python -m scripts.generate_task

# Preview evening push payload
python -m scripts.check_evening

# Send a test notification (requires BARK_TOKEN env var)
BARK_TOKEN=<your_token> python -m scripts.generate_task | python -m scripts.push_bark
```

### Test content pipeline locally / 本地测试内容生成流水线

```bash
# Requires ANTHROPIC_API_KEY env var
export ANTHROPIC_API_KEY=<your_key>

# Run full pipeline (fetches article → generates exercises → outputs Markdown)
python -m scripts.feed_article | python -m scripts.generate_exercises | python -m scripts.commit_content

# Or test each stage independently / 或逐阶段独立测试
python -m scripts.feed_article                           # outputs Article Envelope JSON
python -m scripts.feed_article | python -m scripts.generate_exercises   # outputs Markdown
```

### Trigger GitHub Actions manually / 手动触发 GitHub Actions

```
GitHub repo → Actions → [select workflow] → Run workflow
```

---

## Running Tests / 运行测试

```bash
# All tests
pytest

# Specific file
pytest tests/test_plan_state.py
pytest tests/test_feed_article.py
pytest tests/test_generate_exercises.py
pytest tests/test_commit_content.py

# Verbose output
pytest -v

# With coverage
pytest --cov=scripts
```

---

## Common Issues / 常见问题

### Notification not arriving / 通知未收到

1. Check `BARK_TOKEN` secret is set correctly (token only, no URL prefix).
2. Verify Bark app is installed and notifications are allowed on iPhone.
3. Check Actions tab — look for failed workflow runs.

检查 `BARK_TOKEN` Secret 是否正确设置（仅 token，无 URL 前缀）。
确认 iPhone 上 Bark App 已安装且通知权限已开启。
查看 Actions 标签页是否有失败的工作流。

### Content file not generated / 内容文件未生成

1. Check `ANTHROPIC_API_KEY` secret is set.
2. Check `daily-content.yml` workflow run for error output.
3. Run `python -m scripts.feed_article` locally to verify RSS feed is reachable.

检查 `ANTHROPIC_API_KEY` Secret 是否设置。
查看 `daily-content.yml` 工作流运行日志中的错误输出。
本地运行 `python -m scripts.feed_article` 验证 RSS 源是否可达。

### Duplicate run skipped / 重复运行被跳过

This is expected behavior. If `content/YYYY-MM-DD.md` already exists, `commit_content.py` exits 0 without a new commit.

这是预期行为。若 `content/YYYY-MM-DD.md` 已存在，`commit_content.py` 将干净退出（exit 0），不产生新提交。
