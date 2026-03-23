# AI Provider Configuration / AI 提供商配置

> English · 中文对照

---

## Overview / 概述

This system supports Claude (Anthropic) and OpenAI as interchangeable content generation backends. Both providers are fully integrated with automatic fallback: if the primary provider fails, the system retries automatically with the backup provider — no user action required. Two API keys are supported: `ANTHROPIC_API_KEY` and `OPENAI_API_KEY`. You only need to configure the provider(s) you intend to use, but configuring both enables seamless fallback in either direction.

本系统支持 Claude（Anthropic）和 OpenAI 作为可互换的内容生成后端。两个提供商完全集成并支持自动故障转移：主提供商失败时，系统自动重试备用提供商——无需任何人工干预。支持两个 API 密钥：`ANTHROPIC_API_KEY` 和 `OPENAI_API_KEY`。仅需配置你计划使用的提供商，但同时配置两个可实现双向无缝故障转移。

---

## 1. Get an OpenAI API Key / 获取 OpenAI API Key

Follow these steps to obtain an API key from [platform.openai.com](https://platform.openai.com):

按以下步骤从 [platform.openai.com](https://platform.openai.com) 获取 API key：

1. Visit [platform.openai.com](https://platform.openai.com) and sign in (or create a free account).

   访问 [platform.openai.com](https://platform.openai.com) 并登录（或注册免费账号）。

2. Navigate to **API keys** in the left sidebar (direct link: [platform.openai.com/api-keys](https://platform.openai.com/api-keys)).

   在左侧边栏导航到 **API keys**（直接链接：[platform.openai.com/api-keys](https://platform.openai.com/api-keys)）。

3. Click **Create new secret key**.

   点击 **Create new secret key**。

4. Give the key a name (e.g., `english-daily`), then click **Create secret key**.

   为密钥命名（如 `english-daily`），然后点击 **Create secret key**。

5. Copy the key immediately — it is only shown once. Store it securely (e.g., a password manager).

   立即复制密钥——它只显示一次。请安全存储（如密码管理器）。

**Cost note:** `gpt-4o-mini` (~1,400 tokens/day) costs under $0.01/day at current pricing.

**费用说明：** `gpt-4o-mini`（每天约 1,400 tokens）按当前定价低于 $0.01/天。

---

## 2. Get an Anthropic API Key / 获取 Anthropic API Key

Follow these steps to obtain an API key from [console.anthropic.com](https://console.anthropic.com):

按以下步骤从 [console.anthropic.com](https://console.anthropic.com) 获取 API key：

1. Visit [console.anthropic.com](https://console.anthropic.com) and sign in (or create an account).

   访问 [console.anthropic.com](https://console.anthropic.com) 并登录（或注册账号）。

2. Navigate to **API Keys** in the left sidebar.

   在左侧边栏导航到 **API Keys**。

3. Click **Create Key**.

   点击 **Create Key**。

4. Give the key a name (e.g., `english-daily`), then click **Create Key**.

   为密钥命名（如 `english-daily`），然后点击 **Create Key**。

5. Copy the key immediately — it is only shown once.

   立即复制密钥——它只显示一次。

**Cost note:** `claude-haiku-4-5-20251001` (~1,400 tokens/day) costs under $0.01/day at current pricing.

**费用说明：** `claude-haiku-4-5-20251001`（每天约 1,400 tokens）按当前定价低于 $0.01/天。

---

## 3. Add Keys as GitHub Actions Secrets / 添加为 GitHub Actions Secrets

Both `OPENAI_API_KEY` and `ANTHROPIC_API_KEY` must be added as GitHub Repository Secrets so the CI workflow can access them. Neither key is stored in code or config files.

两个密钥 `OPENAI_API_KEY` 和 `ANTHROPIC_API_KEY` 均须添加为 GitHub 仓库 Secret，以便 CI 工作流访问。两者均不存储在代码或配置文件中。

### Add OPENAI_API_KEY

In your GitHub repository:

在 GitHub 仓库中：

```
Settings → Secrets and variables → Actions → New repository secret
  Name:  OPENAI_API_KEY
  Value: <your OpenAI API key>
```

### Add ANTHROPIC_API_KEY

```
Settings → Secrets and variables → Actions → New repository secret
  Name:  ANTHROPIC_API_KEY
  Value: <your Anthropic API key>
```

Both keys are injected as environment variables in the CI workflow. Neither key is stored in code or config files.

两个密钥均注入为 CI 工作流的环境变量。均不存储在代码或配置文件中。

---

## 4. Provider Priority Rule / 提供商优先级规则

The active provider is determined by a two-level priority (derived from `scripts/ai_provider.py`):

活跃提供商由两级优先级决定（来源：`scripts/ai_provider.py`）：

**Priority (highest to lowest) / 优先级（从高到低）：**

1. `AI_PROVIDER` environment variable — if set and non-empty, always wins.

   `AI_PROVIDER` 环境变量——若已设置且非空，则始终优先。

2. `ai_provider` field in `plan/config.json` — used when the env var is absent (default: `"anthropic"`).

   `plan/config.json` 中的 `ai_provider` 字段——环境变量缺失时使用（默认值：`"anthropic"`）。

### Config file default / 配置文件默认值

```json
{
  "ai_provider": "anthropic",
  "openai_model": "gpt-4o-mini"
}
```

### Override for a single run / 单次覆盖示例

```bash
# Override to OpenAI for one run
AI_PROVIDER=openai python -m scripts.feed_article | python -m scripts.generate_exercises | python -m scripts.commit_content
```

### Automatic fallback / 自动故障转移

If the primary provider fails, the system automatically retries with the backup provider — no user action required. Both keys should be configured so fallback works in either direction.

如果主提供商失败，系统自动重试备用提供商——无需任何人工干预。建议同时配置两个密钥，以支持双向故障转移。

---

## 5. Third-Party Claude API / 第三方 Claude 兼容 API

This system supports any Claude-compatible third-party API endpoint. If you have access to a third-party provider that implements the Anthropic API, you can point `call_claude()` at that endpoint using two optional configuration values: `ANTHROPIC_BASE_URL` and `ANTHROPIC_AUTH_TOKEN`. These are independent of `ANTHROPIC_API_KEY` — you do not need an Anthropic account to use a third-party endpoint.

本系统支持任何兼容 Claude API 的第三方端点。如果你有一个实现了 Anthropic API 的第三方提供商，可以通过两个可选配置值 `ANTHROPIC_BASE_URL` 和 `ANTHROPIC_AUTH_TOKEN` 将 `call_claude()` 指向该端点。这两个值与 `ANTHROPIC_API_KEY` 独立——使用第三方端点无需 Anthropic 账号。

**Priority / 优先级：** Environment variables take highest priority. `plan/config.json` fields are the lower-priority fallback. Unset or empty values cause the system to fall back to standard Anthropic SDK defaults.

**优先级：** 环境变量优先级最高。`plan/config.json` 字段为低优先级回退。未设置或为空时，系统回退到标准 Anthropic SDK 默认行为。

### Option 1: Environment Variables / 方式一：环境变量

Set these environment variables before running any script (or add them as GitHub Secrets — see below):

在运行任意脚本前设置这两个环境变量（或将其添加为 GitHub Secrets——见下文）：

```bash
export ANTHROPIC_BASE_URL="https://your-provider.example.com/v1"
export ANTHROPIC_AUTH_TOKEN="your-provider-auth-token"
```

### Option 2: config.json Fields / 方式二：config.json 字段

Add the optional fields to `plan/config.json`. These are lower priority than env vars — env vars always override them.

将可选字段添加到 `plan/config.json`。这些字段优先级低于环境变量——环境变量始终覆盖它们。

```json
{
  "ai_provider": "anthropic",
  "openai_model": "gpt-4o-mini",
  "anthropic_base_url": "https://your-provider.example.com/v1",
  "anthropic_auth_token": "your-provider-auth-token"
}
```

### Add to GitHub Secrets / 添加为 GitHub Secrets

To use a third-party endpoint in CI, add the two values as GitHub Repository Secrets:

如需在 CI 中使用第三方端点，将两个值添加为 GitHub 仓库 Secret：

```
Settings → Secrets and variables → Actions → New repository secret
  Name:  ANTHROPIC_BASE_URL
  Value: <your third-party endpoint URL>
```

```
Settings → Secrets and variables → Actions → New repository secret
  Name:  ANTHROPIC_AUTH_TOKEN
  Value: <your third-party auth token>
```

If these secrets are absent or empty, the system uses standard Anthropic API defaults — no action required for normal usage.

如果这些 Secret 不存在或为空，系统使用标准 Anthropic API 默认值——正常使用无需任何操作。

---

## Summary / 配置总结

| Secret / 密钥 | Required By / 所需功能 |
|---|---|
| `ANTHROPIC_API_KEY` | Default provider (`anthropic`); fallback when OpenAI is primary |
| `OPENAI_API_KEY` | Required when `AI_PROVIDER=openai` or as fallback for Anthropic |
| `ANTHROPIC_BASE_URL (optional)` | Third-party Claude-compatible endpoint URL / 第三方 Claude 兼容端点 URL |
| `ANTHROPIC_AUTH_TOKEN (optional)` | Auth token for third-party endpoint / 第三方端点认证 token |
