# Configuration Reference / 配置参考

> English · 中文对照

---

## `plan/state.json` — Learning State / 学习状态

**Single source of truth** for the push notification system.

推送通知系统的**唯一数据源**。

```json
{
  "start_date": "YYYY-MM-DD",
  "scene_ratings": {
    "Scene Name": 1
  },
  "daily_log": {
    "YYYY-MM-DD": {
      "completed": ["review", "input"],
      "skipped": false
    }
  }
}
```

| Field / 字段 | Type / 类型 | Description / 说明 |
|--------------|-------------|-------------------|
| `start_date` | `string` | Week 1 Day 1 of your learning plan. All temporal values derive from this. / 学习计划第一周第一天。所有时间值均由此推算。 |
| `scene_ratings` | `object` | Map of scene name → rating (1–5). Used in Weeks 15–16 to auto-select review scene. / 场景名称 → 评分（1–5）映射。第 15–16 周用于自动选择复习场景。 |
| `daily_log` | `object` | Date → completion record. `completed` is a list of done blocks; `skipped` marks the day as skipped. / 日期 → 完成记录。`completed` 是已完成模块列表；`skipped` 标记今日跳过。 |

**Valid block names / 有效模块名：** `review`, `input`, `extraction`, `output`

**Rules / 规则：**
- Never add computed fields (current_week, plan_day, etc.) — derive them at runtime.
- Always use `copy.deepcopy` before mutating state.
- 不要添加计算字段（current_week、plan_day 等）——运行时推算。
- 修改状态前始终使用 `copy.deepcopy`。

---

## `plan/config.json` — System Configuration / 系统配置

Stores push timing, timezone, and RSS feed configuration. **No secrets here.**

存储推送时间、时区和 RSS 源配置。**不存储任何密钥。**

```json
{
  "morning_hour": 7,
  "evening_hour": 21,
  "weekly_recording_day": "saturday",
  "timezone": "Asia/Shanghai",
  "content_feeds": {
    "primary_url": "https://www.newsinlevels.com/feed",
    "fallback_url": "https://www.bbc.co.uk/learningenglish/english/features/lingohack/feed.rss",
    "content_topics": ["AI", "technology", "international", "economy", "science", "climate"]
  }
}
```

| Field / 字段 | Type / 类型 | Description / 说明 |
|--------------|-------------|-------------------|
| `morning_hour` | `int` | Hour (24h) for morning notification in BJT / 早间通知小时（24小时制，北京时间） |
| `evening_hour` | `int` | Hour (24h) for evening notification in BJT / 晚间通知小时（24小时制，北京时间） |
| `weekly_recording_day` | `string` | Day to prompt scene rating (end of 2-week scene) / 提示场景评分的星期（两周场景结束时） |
| `timezone` | `string` | IANA timezone string (display only — code uses hardcoded UTC+8) / IANA 时区字符串（仅展示用——代码使用硬编码 UTC+8） |
| `content_feeds.primary_url` | `string` | Primary RSS feed URL / 主 RSS 源 URL |
| `content_feeds.fallback_url` | `string` | Fallback RSS feed URL (used if primary fails) / 备用 RSS 源 URL（主源失败时使用） |
| `content_feeds.content_topics` | `array[string]` | Keywords for article selection preference / 文章选择偏好关键词 |

### Changing RSS feeds / 更换 RSS 源

Replace `primary_url` or `fallback_url` with any RSS feed that:

替换 `primary_url` 或 `fallback_url` 为任意满足以下条件的 RSS 源：

1. Returns articles with **200+ characters** of body text in `content:encoded`, `summary`, or `description` fields.
2. Is publicly accessible (no auth required).
3. Provides articles in English at B1-B2 reading level.

1. 通过 `content:encoded`、`summary` 或 `description` 字段返回 **200 字符以上**的正文。
2. 可公开访问（无需认证）。
3. 提供 B1-B2 阅读水平的英语文章。

**Verified working feeds / 已验证的可用源：**

| Feed | URL | Notes / 备注 |
|------|-----|-------------|
| News in Levels | `https://www.newsinlevels.com/feed` | Primary; `content:encoded` field, 800+ chars / 主源；`content:encoded` 字段，800+ 字符 |
| BBC Learning English (Lingohack) | `https://www.bbc.co.uk/learningenglish/english/features/lingohack/feed.rss` | Fallback; shorter articles / 备用；文章较短 |

---

## GitHub Secrets / GitHub 密钥

Set via: `Repository Settings → Secrets and variables → Actions`

通过以下路径设置：`仓库设置 → Secrets and variables → Actions`

| Secret / 密钥 | Required By / 所需系统 | Description / 说明 |
|---------------|----------------------|-------------------|
| `BARK_TOKEN` | Push notification system / 推送通知系统 | Bark app token (token only, no URL prefix) / Bark App token（仅 token，不含 URL 前缀） |
| `ANTHROPIC_API_KEY` | Content generation system / 内容生成系统 | Anthropic API key for Claude / Claude 的 Anthropic API key |
| `OPENAI_API_KEY` | Content generation system / 内容生成系统 | OpenAI API key for GPT-4o-mini / GPT-4o-mini 的 OpenAI API key |

**Security rules / 安全规则：**
- Secrets are **only** accessible in GitHub Actions environment variables.
- They are **never** logged, printed, or stored in code or `state.json`.
- The `GITHUB_TOKEN` (automatic) handles git push authentication — no PAT needed.

密钥**仅**在 GitHub Actions 环境变量中可访问。
它们**绝不**被记录、打印或存储在代码或 `state.json` 中。
`GITHUB_TOKEN`（自动生成）处理 git push 认证——无需 PAT。

---

## GitHub Actions Workflows / GitHub Actions 工作流

### `daily-content.yml`

```yaml
on:
  schedule:
    - cron: '0 22 * * *'   # 22:00 UTC = 06:00 BJT next day
  workflow_dispatch:         # manual trigger for testing
```

**Cron explanation / Cron 说明：** `0 22 * * *` = every day at 22:00 UTC = 06:00 BJT (UTC+8 the following calendar day). The Beijing-date file uses the correct BJT date because `get_beijing_date()` computes it explicitly.

`0 22 * * *` = 每天 UTC 22:00 = 北京时间 06:00（UTC+8 的次日）。因为 `get_beijing_date()` 明确计算北京日期，所以生成文件使用正确的北京日期。

### `morning.yml` / `evening.yml`

| Workflow | Cron (UTC) | BJT Time |
|----------|------------|----------|
| `morning.yml` | `0 23 * * *` (approx) | 07:00 |
| `evening.yml` | `0 13 * * *` (approx) | 21:00 |

---

## Scene Roadmap / 场景路线图

Defined in `scripts/plan_state.py` as `SCENE_ROADMAP`. Scene names in `scene_ratings` must match exactly.

在 `scripts/plan_state.py` 中以 `SCENE_ROADMAP` 定义。`scene_ratings` 中的场景名称必须完全匹配。

| Weeks / 周次 | Scene / 场景 |
|-------------|-------------|
| 1–2 | 自我介绍 & 日常寒暄 |
| 3–4 | 表达观点 & 讨论方案 |
| 5–6 | 邮件写作 & 职场书面表达 |
| 7–8 | 制定计划 & 社交对话 |
| 9–10 | 汇报进展 & 给出反馈 |
| 11–12 | 表达情绪 & 讲故事 |
| 13–14 | 提问确认 & 信息核实 |
| 15–16 | 自由复习（自动选评分最低场景）|
