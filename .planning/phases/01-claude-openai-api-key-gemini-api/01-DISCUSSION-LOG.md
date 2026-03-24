# Phase 1: Gemini Migration - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-03-24
**Phase:** 01-claude-openai-api-key-gemini-api

---

## Area 1: Gemini SDK Choice

**Question:** Which Gemini SDK approach?

| Option | Description |
|--------|-------------|
| google-genai ✓ | 官方新 SDK，Client 模式，Google 长期支持方向 |
| google-generativeai | 旧稳定 SDK，文档较多，但 Google 已标记迁移 |
| OpenAI-compatible endpoint | 复用现有 openai SDK，代码改动最少，但非原生 |

**Selected:** `google-genai`

**Revisited:** Yes（用户确认了一次）— 最终保持 `google-genai`

---

## Area 2: Model Selection

**Question:** Which Gemini model to use?

| Option | Cost | Notes |
|--------|------|-------|
| gemini-2.0-flash-lite ✓ | $0.075/$0.30 per 1M tokens | 最便宜，适合每天一次 |
| gemini-2.0-flash | $0.10/$0.40 per 1M tokens | 更快更好，成本略高 |
| gemini-1.5-flash | 部分免费 | 上一代，不推荐新项目 |

**Selected:** `gemini-2.0-flash-lite`

---

## Area 3: Fallback Handling

**Question:** With only one provider, remove fallback logic?

| Option | Notes |
|--------|-------|
| Remove entirely ✓ | 简化代码，单一 provider 无需 retry |
| Keep simplified framework | 保留扩展空间 |

**Selected:** Remove entirely

---

## Area 4: Env Var / Config Naming

**Question:** Env var and config naming for Gemini?

| Option | Env var | Config field |
|--------|---------|--------------|
| GEMINI_API_KEY ✓ | GEMINI_API_KEY | gemini_model |
| GOOGLE_API_KEY | GOOGLE_API_KEY | gemini_model |

**Selected:** `GEMINI_API_KEY` + `gemini_model`

---

## Area 5: 中文输出

**Question:** 中文输出 是指什么？

**Selected:** 只是备注，不是功能需求（不需要修改代码逻辑）
