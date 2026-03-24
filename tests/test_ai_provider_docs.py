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
            "Create the file to satisfy documentation requirements."
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
# Gemini API key instructions
# ---------------------------------------------------------------------------


def test_gemini_studio_url_present(docs_content: str):
    assert "aistudio.google.com" in docs_content, (
        "docs/ai-providers.md must contain 'aistudio.google.com'"
    )


def test_gemini_secret_documented(docs_content: str):
    assert "GEMINI_API_KEY" in docs_content, (
        "docs/ai-providers.md must contain 'GEMINI_API_KEY'"
    )


# ---------------------------------------------------------------------------
# Model configuration
# ---------------------------------------------------------------------------


def test_gemini_model_field_documented(docs_content: str):
    assert "gemini_model" in docs_content, (
        "docs/ai-providers.md must contain 'gemini_model' (config.json field)"
    )


def test_default_model_documented(docs_content: str):
    assert "gemini-2.5-flash-lite" in docs_content, (
        "docs/ai-providers.md must contain 'gemini-2.5-flash-lite'"
    )


# ---------------------------------------------------------------------------
# API key priority rule
# ---------------------------------------------------------------------------


def test_priority_rule_env_var(docs_content: str):
    assert "GEMINI_API_KEY" in docs_content, (
        "docs/ai-providers.md must contain 'GEMINI_API_KEY' env var documentation"
    )


# ---------------------------------------------------------------------------
# Summary table
# ---------------------------------------------------------------------------


def test_summary_table_has_gemini_key(docs_content: str):
    assert "GEMINI_API_KEY" in docs_content, (
        "docs/ai-providers.md summary table must contain 'GEMINI_API_KEY'"
    )


# ---------------------------------------------------------------------------
# No old provider references in docs
# ---------------------------------------------------------------------------


def test_no_openai_url(docs_content: str):
    assert "platform.openai.com" not in docs_content, (
        "docs/ai-providers.md must not reference 'platform.openai.com' (old provider)"
    )


def test_no_anthropic_console_url(docs_content: str):
    assert "console.anthropic.com" not in docs_content, (
        "docs/ai-providers.md must not reference 'console.anthropic.com' (old provider)"
    )
