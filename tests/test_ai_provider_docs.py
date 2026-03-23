from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# Module-level fixture — reads docs/ai-providers.md once, shared by all tests
# ---------------------------------------------------------------------------

DOCS_FILE = Path(__file__).parent.parent / "docs" / "ai-providers.md"


@pytest.fixture(scope="module")
def docs_content() -> str:
    if not DOCS_FILE.exists():
        raise FileNotFoundError(
            f"docs/ai-providers.md not found at {DOCS_FILE}. "
            "Create the file to satisfy DOCS-01 through DOCS-04."
        )
    return DOCS_FILE.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# File existence (prerequisite)
# ---------------------------------------------------------------------------


def test_docs_file_exists():
    assert DOCS_FILE.exists(), (
        f"docs/ai-providers.md does not exist at {DOCS_FILE}"
    )


# ---------------------------------------------------------------------------
# DOCS-01 — OpenAI API key instructions
# ---------------------------------------------------------------------------


def test_openai_url_present(docs_content: str):
    assert "platform.openai.com" in docs_content, (
        "DOCS-01: docs/ai-providers.md must contain 'platform.openai.com'"
    )


# ---------------------------------------------------------------------------
# DOCS-02 — Anthropic API key instructions
# ---------------------------------------------------------------------------


def test_anthropic_url_present(docs_content: str):
    assert "console.anthropic.com" in docs_content, (
        "DOCS-02: docs/ai-providers.md must contain 'console.anthropic.com'"
    )


# ---------------------------------------------------------------------------
# DOCS-03 — GitHub Actions Secrets for both providers
# ---------------------------------------------------------------------------


def test_openai_secret_documented(docs_content: str):
    assert "OPENAI_API_KEY" in docs_content, (
        "DOCS-03: docs/ai-providers.md must contain 'OPENAI_API_KEY'"
    )


def test_anthropic_secret_documented(docs_content: str):
    assert "ANTHROPIC_API_KEY" in docs_content, (
        "DOCS-03: docs/ai-providers.md must contain 'ANTHROPIC_API_KEY'"
    )


# ---------------------------------------------------------------------------
# DOCS-04 — Provider priority rule
# ---------------------------------------------------------------------------


def test_priority_rule_env_var(docs_content: str):
    assert "AI_PROVIDER" in docs_content, (
        "DOCS-04: docs/ai-providers.md must contain 'AI_PROVIDER' (env var)"
    )


def test_priority_rule_config_field(docs_content: str):
    assert "ai_provider" in docs_content, (
        "DOCS-04: docs/ai-providers.md must contain 'ai_provider' (config.json field)"
    )


# ---------------------------------------------------------------------------
# v1.2 DOCS-01 — Third-party Claude API section (bilingual)
# ---------------------------------------------------------------------------


def test_section5_exists(docs_content: str):
    assert "## 5. Third-Party Claude API" in docs_content, (
        "DOCS-01: docs/ai-providers.md must contain '## 5. Third-Party Claude API'"
    )


def test_third_party_bilingual(docs_content: str):
    assert "第三方 Claude 兼容 API" in docs_content, (
        "DOCS-01: docs/ai-providers.md must contain Chinese translation '第三方 Claude 兼容 API'"
    )


# ---------------------------------------------------------------------------
# v1.2 DOCS-02 — config.json example with anthropic_base_url / anthropic_auth_token
# ---------------------------------------------------------------------------


def test_config_example_fields(docs_content: str):
    assert "anthropic_base_url" in docs_content, (
        "DOCS-02: docs/ai-providers.md must contain 'anthropic_base_url' in config example"
    )
    assert "anthropic_auth_token" in docs_content, (
        "DOCS-02: docs/ai-providers.md must contain 'anthropic_auth_token' in config example"
    )


# ---------------------------------------------------------------------------
# v1.2 DOCS-03 — GitHub Secrets section for ANTHROPIC_BASE_URL / ANTHROPIC_AUTH_TOKEN
# ---------------------------------------------------------------------------


def test_github_secrets_section(docs_content: str):
    assert "ANTHROPIC_BASE_URL" in docs_content, (
        "DOCS-03: docs/ai-providers.md must contain 'ANTHROPIC_BASE_URL'"
    )
    assert "ANTHROPIC_AUTH_TOKEN" in docs_content, (
        "DOCS-03: docs/ai-providers.md must contain 'ANTHROPIC_AUTH_TOKEN'"
    )


def test_summary_table_optional_rows(docs_content: str):
    assert "ANTHROPIC_BASE_URL (optional)" in docs_content, (
        "DOCS-03: Summary table must contain 'ANTHROPIC_BASE_URL (optional)'"
    )
    assert "ANTHROPIC_AUTH_TOKEN (optional)" in docs_content, (
        "DOCS-03: Summary table must contain 'ANTHROPIC_AUTH_TOKEN (optional)'"
    )
