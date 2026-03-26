# System Architecture / 系统架构

> English · 中文对照

---

## Overview / 概览

This repository contains **two independent systems** sharing the same codebase and CI infrastructure.

本仓库包含**两个独立系统**，共享同一套代码库和 CI 基础设施。

| System / 系统 | Purpose / 用途 | Trigger / 触发方式 |
|---------------|---------------|------------------|
| **Push Notification System** / 推送通知系统 | Sends daily learning task reminders to iPhone via Bark | Morning 07:00 + Evening 21:00 BJT cron |
| **Content Generation System** / 内容生成系统 | Fetches real English articles, generates AI exercises, commits Markdown lesson files | Daily 06:00 BJT cron |

---

## System 1: Push Notification Pipeline / 推送通知流水线

```
plan/state.json
      │
      ▼
generate_task.py   ──stdout JSON──▶  push_bark.py  ──▶  iPhone (Bark)
check_evening.py   ──stdout JSON──▶  push_bark.py  ──▶  iPhone (Bark)
```

**Data flow / 数据流：**

- `plan/state.json` is the single source of truth for learning state.
- `plan_state.py` derives all temporal values (current week, scene, day) from `start_date` at runtime — nothing is stored pre-computed.
- Scripts communicate via JSON envelope on stdout: `{"title": str, "body": str, "url": str | null}`

`plan/state.json` 是学习状态的唯一数据源。
`plan_state.py` 每次运行时从 `start_date` 实时推算所有时间值（当前周次、场景、天数）——不预先存储计算结果。
脚本之间通过 stdout JSON 信封传递数据：`{"title": str, "body": str, "url": str | null}`

---

## System 2: Content Generation Pipeline / 内容生成流水线

```
RSS Feed (newsinlevels.com)
           │  feedparser
           ▼
   feed_article.py
   ┌─────────────────────────────────────┐
   │  fetch → validate → select entry    │
   │  fallback: BBC Learning English     │
   └─────────────────────────────────────┘
           │ Article Envelope JSON (stdout)
           │ {"title": str, "body": str, "source_url": str}
           ▼
  generate_exercises.py
  ┌──────────────────────────────────────────────────────┐
  │  build_prompt → call_claude → parse_response         │
  │  → render_markdown                                   │
  │  Model: claude-3-5-haiku-20241022 (1 call/day)       │
  └──────────────────────────────────────────────────────┘
           │ Full Markdown lesson (stdout)
           ▼
   commit_content.py
   ┌─────────────────────────────────────────────────────┐
   │  idempotency check → write file → git commit+push   │
   │  Output: content/YYYY-MM-DD.md (Beijing date)       │
   └─────────────────────────────────────────────────────┘
```

**Pipeline invocation in CI (with `set -eo pipefail`) / CI 中的流水线调用：**

```bash
set -eo pipefail
python -m scripts.feed_article | \
python -m scripts.generate_exercises | \
python -m scripts.commit_content
```

`set -eo pipefail` ensures that if any stage exits non-zero, the entire pipeline fails and CI marks the job as failed.

`set -eo pipefail` 确保任意阶段退出非零时，整个流水线失败，CI 将任务标记为失败。

---

## Key Design Decisions / 关键设计决策

### Beijing Timezone / 北京时区

```python
# CORRECT: derives Beijing date even on UTC runners
# 正确：即使在 UTC 服务器上也能推算北京日期
BEIJING_TZ = timezone(timedelta(hours=8))
get_beijing_date() → datetime.now(tz=BEIJING_TZ).date()

# WRONG: returns UTC date on GitHub Actions runners
# 错误：在 GitHub Actions 服务器上返回 UTC 日期
date.today()
```

### Idempotency / 幂等性

```python
# If today's file already exists, exit 0 cleanly (no duplicate commit)
# 若今天的文件已存在，干净地退出 0（不产生重复提交）
if content_path(today).exists():
    sys.exit(0)
```

### Testability / 可测试性

SDK clients are instantiated **inside** functions, not at module level. This allows clean patching in unit tests without module-level state.

SDK 客户端在**函数内部**实例化，不在模块级别。这样可在单元测试中干净地打桩，避免模块级状态。

```python
# CORRECT / 正确
def call_claude(prompt: str) -> str:
    client = anthropic.Anthropic()   # inside function
    ...

# WRONG / 错误
client = anthropic.Anthropic()       # module level — hard to mock
```

### Immutability / 不可变性

`state.json` mutations always use `copy.deepcopy`.

`state.json` 的修改始终使用 `copy.deepcopy`。

---

## File Structure / 文件结构

```
study-all/
├── plan/
│   ├── state.json          # Learning state (start_date, daily_log, ratings)
│   │                       # 学习状态（开始日期、完成记录、场景评分）
│   └── config.json         # Push times, timezone, RSS feed URLs
│                           # 推送时间、时区、RSS 源 URL
├── scripts/
│   ├── content_utils.py    # Shared: Beijing timezone, content_path()
│   │                       # 共用：北京时区、内容路径
│   ├── feed_article.py     # RSS fetch → Article Envelope JSON
│   │                       # RSS 抓取 → 文章信封 JSON
│   ├── generate_exercises.py  # Claude AI → Markdown lesson
│   │                          # Claude AI → Markdown 课程
│   ├── commit_content.py   # Idempotency check + git commit
│   │                       # 幂等检查 + git 提交
│   ├── plan_state.py       # Temporal calculations + state I/O
│   │                       # 时间计算 + 状态读写
│   ├── generate_task.py    # Morning push payload builder
│   │                       # 早间推送内容构建
│   ├── check_evening.py    # Evening push payload builder
│   │                       # 晚间推送内容构建
│   ├── push_bark.py        # Bark API client
│   │                       # Bark API 客户端
├── content/                # Generated lesson files (git-committed)
│   └── YYYY-MM-DD.md       # 已生成的课程文件（已提交到 git）
├── tests/                  # Pytest unit tests
│   └── ...                 # 单元测试
└── .github/workflows/
    ├── daily-content.yml   # 06:00 BJT — generate & commit lesson
    │                       # 每天 06:00 BJT — 生成并提交课程
    ├── morning.yml         # 07:00 BJT — morning push notification
    │                       # 每天 07:00 BJT — 早间推送通知
    └── evening.yml         # 21:00 BJT — evening push notification
                            # 每天 21:00 BJT — 晚间推送通知
```
