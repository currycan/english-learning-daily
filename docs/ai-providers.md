# AI Provider Configuration / AI 提供商配置

> English · 中文对照

---

## Overview / 概述

This system uses Google Gemini as the AI provider for content generation. A single `GEMINI_API_KEY` is required. The model is configurable via `plan/config.json` (`gemini_model` field) and defaults to `gemini-2.0-flash-lite`.

本系统使用 Google Gemini 作为内容生成 AI 提供商。仅需一个 `GEMINI_API_KEY`。模型可通过 `plan/config.json` 的 `gemini_model` 字段配置，默认为 `gemini-2.0-flash-lite`。

---

## 1. Get a Gemini API Key / 获取 Gemini API Key

Follow these steps to obtain an API key from [aistudio.google.com](https://aistudio.google.com):

按以下步骤从 [aistudio.google.com](https://aistudio.google.com) 获取 API key：

1. Visit [aistudio.google.com](https://aistudio.google.com) and sign in with your Google account.

   访问 [aistudio.google.com](https://aistudio.google.com) 并使用 Google 账号登录。

2. Click **Get API key** in the left sidebar.

   在左侧边栏点击 **Get API key**。

3. Click **Create API key**.

   点击 **Create API key**。

4. Select a Google Cloud project (or create a new one), then click **Create API key in existing project**.

   选择一个 Google Cloud 项目（或新建），然后点击 **Create API key in existing project**。

5. Copy the key immediately and store it securely (e.g., a password manager).

   立即复制密钥并安全存储（如密码管理器）。

**Cost note:** `gemini-2.0-flash-lite` (~1,400 tokens/day) costs under $0.01/day at current pricing. Google AI Studio provides a free tier.

**费用说明：** `gemini-2.0-flash-lite`（每天约 1,400 tokens）按当前定价低于 $0.01/天。Google AI Studio 提供免费配额。

---

## 2. Add Key as GitHub Actions Secret / 添加为 GitHub Actions Secret

`GEMINI_API_KEY` must be added as a GitHub Repository Secret so the CI workflow can access it. The key is never stored in code or config files.

`GEMINI_API_KEY` 必须添加为 GitHub 仓库 Secret，以便 CI 工作流访问。密钥不存储在代码或配置文件中。

### Add GEMINI_API_KEY

In your GitHub repository:

在 GitHub 仓库中：

```
Settings → Secrets and variables → Actions → New repository secret
  Name:  GEMINI_API_KEY
  Value: <your Gemini API key>
```

The key is injected as an environment variable in the CI workflow step that generates content.

密钥注入为 CI 工作流内容生成步骤的环境变量。

---

## 3. Model Configuration / 模型配置

The Gemini model is configured via `plan/config.json`. The `gemini_model` field specifies which model to use:

Gemini 模型通过 `plan/config.json` 配置。`gemini_model` 字段指定要使用的模型：

```json
{
  "gemini_model": "gemini-2.0-flash-lite"
}
```

To override the model for a single run, use the `model` parameter of `call_gemini()` or update `plan/config.json`.

如需单次覆盖模型，可修改 `plan/config.json` 中的 `gemini_model` 字段。

---

## 4. API Key Priority / API Key 优先级

`call_gemini()` resolves the API key in this order:

`call_gemini()` 按以下顺序解析 API key：

**Priority (highest to lowest) / 优先级（从高到低）：**

1. `GEMINI_API_KEY` environment variable — if set and non-empty, always wins.

   `GEMINI_API_KEY` 环境变量——若已设置且非空，则始终优先。

2. `api_key` parameter passed directly to `call_gemini()`.

   直接传入 `call_gemini()` 的 `api_key` 参数。

3. Empty string (will result in API auth error if no key is configured).

   空字符串（若未配置密钥，将导致 API 认证错误）。

---

## Summary / 配置总结

| Secret / 密钥 | Required By / 所需功能 |
|---|---|
| `GEMINI_API_KEY` | Required for all content generation / 内容生成必须 |
