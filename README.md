# English Learning Daily

**网站：[english.ansandy.com](https://english.ansandy.com)**

每天自动生成英语学习任务，通过 [Bark](https://bark.day.app/) 推送到 iPhone。

- 早上 07:00 推送当天任务（复习 / 听力 / 阅读 / 口语输出）
- 晚上 21:00 推送完成情况 + 明日预告
- 每天 06:00 自动抓取英语新闻，调用 Gemini AI 生成词汇、表达和理解练习，提交到 `content/YYYY-MM-DD.md`
- 每两周场景结束时提醒评分，用于后期复习场景的选择

## 学习计划

16 周 / 8 个场景，每个场景两周，每天 35–45 分钟：

| 周次  | 场景                          |
|-------|-------------------------------|
| 1–2   | 自我介绍 & 日常寒暄           |
| 3–4   | 表达观点 & 讨论方案           |
| 5–6   | 邮件写作 & 职场书面表达       |
| 7–8   | 制定计划 & 社交对话           |
| 9–10  | 汇报进展 & 给出反馈           |
| 11–12 | 表达情绪 & 讲故事             |
| 13–14 | 提问确认 & 信息核实           |
| 15–16 | 自由复习（自动选评分最低场景）|

每天四个模块：

- **Review（5min）**：Anki 复习当日到期卡片
- **Input（15min）**：播客片段，三遍听：理解 → 跟读节奏 → 跟读语调
- **Extraction（10min）**：文章精读，摘录 3–5 个地道表达加入 Anki
- **Output（10–15min）**：将推送中的 prompt 发给 Claude / ChatGPT 进行对话练习

## 快速开始

### 1. Fork 本仓库

### 2. 设置 Bark Token

打开 iPhone 上的 Bark app，复制首页显示的 token，然后在 GitHub 仓库中添加 Secret：

Settings → Secrets and variables → Actions → New repository secret

- Name: `BARK_TOKEN`
- Value: 你的 Bark token（仅 token，不含 URL）

### 3. 设置每日英语内容（可选）

每日内容生成需要 Gemini API Key。在 [Google AI Studio](https://aistudio.google.com/) 获取后添加 Secret：

- Name: `GEMINI_API_KEY`
- Value: 你的 Gemini API key

不设置此 Secret 时，推送功能正常运行，但 `content/` 目录不会生成每日文章。

### 4. 设置计划开始日期

编辑 `plan/state.json`，将 `start_date` 改为你想开始的日期：

```json
{
  "start_date": "2026-03-21",
  "scene_ratings": {},
  "daily_log": {}
}
```

### 5. 启用 GitHub Actions

确保仓库的 Actions 已启用（Settings → Actions → Allow all actions）。之后每天自动触发，无需手动操作。

## 手动触发推送

在 GitHub 仓库页面 → Actions → 选择对应 workflow → Run workflow。

## 项目结构

```
├── plan/
│   ├── state.json          # 学习进度（start_date、完成记录、场景评分）
│   └── config.json         # 推送时间、时区、RSS 源及 Gemini 模型配置
├── scripts/
│   ├── plan_state.py       # 状态读写与时间计算
│   ├── generate_task.py    # 生成早间推送内容
│   ├── check_evening.py    # 生成晚间推送内容
│   ├── push_bark.py        # 调用 Bark API 发送通知
│   ├── feed_article.py     # 从 RSS 源抓取英语文章
│   ├── generate_exercises.py  # 调用 Gemini AI 生成词汇/表达/理解练习
│   ├── commit_content.py   # 将生成内容写入 content/ 并提交
│   ├── ai_provider.py      # Gemini API 封装
│   └── content_utils.py    # 内容路径与日期工具函数
├── content/
│   └── YYYY-MM-DD.md       # 每日自动生成的英语文章练习
└── .github/workflows/
    ├── morning.yml          # 每天 07:00 BJT 触发
    ├── evening.yml          # 每天 21:00 BJT 触发
    └── daily-content.yml    # 每天 06:00 BJT 触发，生成每日内容
```

## 每日英语内容 / Daily English Content

系统每天 06:00（北京时间）自动抓取一篇真实英语新闻（News in Levels 为主，BBC Learning English 为备选），调用 Gemini 2.5 Flash Lite 生成：

- **词汇（5–8 个）**：词性、中文释义、英文释义、原文例句
- **地道表达（3–5 个）**：用法说明和生成例句
- **理解题（3–5 道）**：含至少一道推理题，附中英文答案

结果提交到 `content/YYYY-MM-DD.md`，可直接在仓库浏览。

In addition to push notifications, the system fetches a real English article daily at 06:00 BJT, uses Gemini AI to generate vocabulary, chunking expressions, and comprehension exercises, and commits the result to `content/YYYY-MM-DD.md`.

**Additional setup required:** Add `GEMINI_API_KEY` to GitHub Secrets.

详见 → [docs/content-pipeline.md](docs/content-pipeline.md)

## 文档 / Documentation

| 文档 | Doc | 说明 |
|------|-----|------|
| [docs/setup-guide.md](docs/setup-guide.md) | Setup Guide | 完整部署步骤（推送 + 内容生成）/ Full deployment steps |
| [docs/architecture.md](docs/architecture.md) | Architecture | 系统架构与设计决策 / System architecture & design decisions |
| [docs/content-pipeline.md](docs/content-pipeline.md) | Content Pipeline | 每日内容生成流水线详解 / Daily content pipeline deep-dive |
| [docs/script-reference.md](docs/script-reference.md) | Script Reference | 所有脚本的 API 参考 / All scripts API reference |
| [docs/configuration.md](docs/configuration.md) | Configuration | 配置文件格式与参数说明 / Config file format & parameters |

## 依赖

- Python 3.12+
- `requests`（调用 Bark API）
- `feedparser`（解析 RSS 源）
- `google-genai`（调用 Gemini API 生成练习）
- GitHub Actions（定时触发）
- [Bark](https://bark.day.app/)（iOS 推送）
