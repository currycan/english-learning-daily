# Phase 03: Lesson Reading Experience - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-03-24
**Phase:** 03-lesson-reading-experience
**Areas discussed:** Homepage depth, Recent list details, No-content notice, Section collapse UX

---

## Homepage Depth

| Option | Description | Selected |
|--------|-------------|----------|
| 完整课文 + 可折叠区块 | 首页内联展示完整课文：文章全文（始终可见）+ 词汇/表达/问题（折叠态）。用户不需要跳转即可学习。 | ✓ |
| 仅文章正文 + 跳转链接 | 首页只展示文章文本，底部有「查看词汇与习题 →」链接跳转到课文详情页。首页更简洁，但词汇练习需要额外点击。 | |
| 文章摘要 + 跳转 | 首页只展示文章前几段（预览），点击进入完整课文页面。适合日后文章较长的情况，但现在内容较短可能显得奇怪。 | |

**User's choice:** 完整课文内联 + 原文跳转链接（用户要求两者都集成）
**Notes:** 用户明确希望"完整课文内联"和"原文跳转"都集成。原文链接从课文 `> Source: URL` 提取，渲染为"阅读原文 →"链接。

---

## Recent List Details

### 每条信息格式

| Option | Description | Selected |
|--------|-------------|----------|
| 日期 + 文章开头一句 | 例如「2026-03-23 · Paris has a big problem with trash, and it is...」 | ✓ |
| 仅日期 | 例如「2026-03-23」，简洁。 | |
| 日期 + 文章标题 | 从文章第一行提取标题，信息量适中。 | |

**User's choice:** 日期 + 文章开头一句

### 展示条数

| Option | Description | Selected |
|--------|-------------|----------|
| 5 天 | LESS-02 要求范围是 5–7 天，5 比较简洁 | ✓ |
| 7 天 | 展示一整周的历史记录 | |

**User's choice:** 5 条

---

## No-Content Notice

| Option | Description | Selected |
|--------|-------------|----------|
| 展示昨日课文 + 标注提示 | 首页主区展示最新可用课文（通常是昨天），顶部显示一条小提示条「今日课文将在中午更新」。页面不空。 | ✓ |
| 空白主区 + 提示文字 | 首页主区显示「今日课文将在中午更新」占位符，下方紧接最近课文列表。焦点感更强。 | |

**User's choice:** 展示昨日课文 + 标注提示

---

## Section Collapse UX

| Option | Description | Selected |
|--------|-------------|----------|
| HTML `<details>` 原生实现 | 无 JS，访问性好，无动画。对个人学习工具完全足够。 | |
| JS 驱动，带动画 | 平滑展开/收起动画，但需要少量 JavaScript。 | ✓ |

**User's choice:** JS 驱动，带动画

---

## Claude's Discretion

- 动画时长/缓动曲线
- Source URL 的提取方式（正则 vs Markdown 解析）
- 内部组件结构（单页组件 vs 独立 Astro 组件）
- 词汇条目的卡片样式具体设计（website-CONTEXT.md 已定为 "styled definition card"）
- 提示条（"⚠️ 今日课文将在中午更新"）的具体样式

## Deferred Ideas

- 《新概念英语 2-3》内容集成 — 用户提出，属于新能力（内容来源扩展），延迟到未来 Phase
