import os
from unittest.mock import patch, MagicMock
import pytest
import anthropic
import scripts.ai_provider as ap


# ---------------------------------------------------------------------------
# resolve_provider tests
# ---------------------------------------------------------------------------


def test_resolve_provider_env_var_priority(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "openai")
    result = ap.resolve_provider({"ai_provider": "anthropic"})
    assert result == "openai"


def test_resolve_provider_config_default(monkeypatch):
    monkeypatch.delenv("AI_PROVIDER", raising=False)
    result = ap.resolve_provider({"ai_provider": "openai"})
    assert result == "openai"


def test_resolve_provider_anthropic_default(monkeypatch):
    monkeypatch.delenv("AI_PROVIDER", raising=False)
    result = ap.resolve_provider({})
    assert result == "anthropic"


def test_resolve_provider_unknown_exits(monkeypatch):
    monkeypatch.delenv("AI_PROVIDER", raising=False)
    with pytest.raises(SystemExit) as exc_info:
        ap.resolve_provider({"ai_provider": "foobar"})
    assert exc_info.value.code == 1


def test_resolve_provider_env_unknown_exits(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "badvalue")
    with pytest.raises(SystemExit) as exc_info:
        ap.resolve_provider({})
    assert exc_info.value.code == 1


# ---------------------------------------------------------------------------
# call_openai tests
# ---------------------------------------------------------------------------


def test_call_openai_returns_content():
    with patch("scripts.ai_provider.openai.OpenAI") as MockOpenAI:
        mock_client = MagicMock()
        MockOpenAI.return_value = mock_client
        mock_client.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content='{"vocabulary":[],"chunks":[],"questions":[]}'))]
        )
        result = ap.call_openai("test prompt", model="gpt-4o-mini")
    assert result == '{"vocabulary":[],"chunks":[],"questions":[]}'


def test_call_openai_uses_configured_model():
    with patch("scripts.ai_provider.openai.OpenAI") as MockOpenAI:
        mock_client = MagicMock()
        MockOpenAI.return_value = mock_client
        mock_client.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="response"))]
        )
        ap.call_openai("test prompt", model="gpt-4o-mini")
    call_kwargs = mock_client.chat.completions.create.call_args
    # Works whether called with positional or keyword args
    called_model = call_kwargs.kwargs.get("model") or (call_kwargs.args[0] if call_kwargs.args else None)
    assert called_model == "gpt-4o-mini"


def test_call_openai_raises_provider_error_on_error():
    with patch("scripts.ai_provider.openai.OpenAI") as MockOpenAI:
        mock_client = MagicMock()
        MockOpenAI.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("err")
        with pytest.raises(ap.ProviderError):
            ap.call_openai("test prompt", model="gpt-4o-mini")


# ---------------------------------------------------------------------------
# call_claude tests
# ---------------------------------------------------------------------------


def test_call_claude_raises_provider_error_on_api_error():
    with patch("scripts.ai_provider.anthropic.Anthropic") as MockAnthropic:
        mock_client = MagicMock()
        MockAnthropic.return_value = mock_client
        mock_client.messages.create.side_effect = anthropic.APIError(
            message="err", request=MagicMock(), body=None
        )
        with pytest.raises(ap.ProviderError):
            ap.call_claude("prompt")


# ---------------------------------------------------------------------------
# call_ai dispatch tests
# ---------------------------------------------------------------------------


def test_call_ai_dispatches_anthropic():
    with patch("scripts.ai_provider.call_claude") as mock_call_claude:
        mock_call_claude.return_value = "claude response"
        ap.call_ai("p", provider="anthropic", model_config={"openai_model": "gpt-4o-mini"})
    mock_call_claude.assert_called_once()


def test_call_ai_dispatches_openai():
    with patch("scripts.ai_provider.call_openai") as mock_call_openai:
        mock_call_openai.return_value = "openai response"
        ap.call_ai("p", provider="openai", model_config={"openai_model": "gpt-4o-mini"})
    mock_call_openai.assert_called_once()
    call_kwargs = mock_call_openai.call_args
    assert call_kwargs.kwargs.get("model") == "gpt-4o-mini"


# ---------------------------------------------------------------------------
# fallback tests (FALL-01, FALL-02, FALL-03, TEST-02)
# ---------------------------------------------------------------------------


def test_call_ai_fallback_primary_fails_backup_succeeds():
    with patch("scripts.ai_provider.call_claude") as mock_claude, \
         patch("scripts.ai_provider.call_openai") as mock_openai:
        mock_claude.side_effect = ap.ProviderError("claude down")
        mock_openai.return_value = "openai response"
        result = ap.call_ai("prompt", provider="anthropic", model_config={"openai_model": "gpt-4o-mini"})
    assert result == "openai response"
    mock_openai.assert_called_once()


def test_call_ai_fallback_openai_primary_fails():
    with patch("scripts.ai_provider.call_openai") as mock_openai, \
         patch("scripts.ai_provider.call_claude") as mock_claude:
        mock_openai.side_effect = ap.ProviderError("openai down")
        mock_claude.return_value = "claude response"
        result = ap.call_ai("prompt", provider="openai", model_config={"openai_model": "gpt-4o-mini"})
    assert result == "claude response"
    mock_claude.assert_called_once()


def test_call_ai_fallback_both_fail_exits():
    with patch("scripts.ai_provider.call_claude") as mock_claude, \
         patch("scripts.ai_provider.call_openai") as mock_openai:
        mock_claude.side_effect = ap.ProviderError("claude down")
        mock_openai.side_effect = ap.ProviderError("openai down")
        with pytest.raises(SystemExit) as exc_info:
            ap.call_ai("prompt", provider="anthropic", model_config={"openai_model": "gpt-4o-mini"})
    assert exc_info.value.code == 1


def test_call_ai_fallback_logs_to_stderr(capsys):
    with patch("scripts.ai_provider.call_claude") as mock_claude, \
         patch("scripts.ai_provider.call_openai") as mock_openai:
        mock_claude.side_effect = ap.ProviderError("claude down")
        mock_openai.return_value = "ok"
        ap.call_ai("prompt", provider="anthropic", model_config={"openai_model": "gpt-4o-mini"})
    captured = capsys.readouterr()
    assert "anthropic" in captured.err
    assert "openai" in captured.err


def test_backup_provider_anthropic_returns_openai():
    assert ap._backup_provider("anthropic") == "openai"


def test_backup_provider_openai_returns_anthropic():
    assert ap._backup_provider("openai") == "anthropic"


# ---------------------------------------------------------------------------
# call_claude custom endpoint tests (TPROV-01, TPROV-02, TPROV-03, CONF-01–CONF-03, TEST-01, TEST-02)
# ---------------------------------------------------------------------------


def test_call_claude_uses_custom_base_url_and_auth_token(monkeypatch):
    """TEST-01 / TPROV-01 / TPROV-02 / CONF-01 / CONF-02:
    When ANTHROPIC_BASE_URL and ANTHROPIC_AUTH_TOKEN env vars are set,
    anthropic.Anthropic() must be called with base_url and api_key."""
    monkeypatch.setenv("ANTHROPIC_BASE_URL", "https://custom.example.com")
    monkeypatch.setenv("ANTHROPIC_AUTH_TOKEN", "custom-token-123")
    with patch("scripts.ai_provider.anthropic.Anthropic") as MockAnthropic:
        mock_client = MagicMock()
        MockAnthropic.return_value = mock_client
        mock_client.messages.create.return_value = MagicMock(
            content=[MagicMock(text="response")]
        )
        ap.call_claude("prompt")
    MockAnthropic.assert_called_once_with(
        base_url="https://custom.example.com",
        api_key="custom-token-123",
    )


def test_call_claude_backward_compat_no_custom_config(monkeypatch):
    """TEST-02 / TPROV-03:
    When no custom env vars or kwargs are present, anthropic.Anthropic()
    must be called with no arguments (identical to v1.1 behavior)."""
    monkeypatch.delenv("ANTHROPIC_BASE_URL", raising=False)
    monkeypatch.delenv("ANTHROPIC_AUTH_TOKEN", raising=False)
    with patch("scripts.ai_provider.anthropic.Anthropic") as MockAnthropic:
        mock_client = MagicMock()
        MockAnthropic.return_value = mock_client
        mock_client.messages.create.return_value = MagicMock(
            content=[MagicMock(text="response")]
        )
        ap.call_claude("prompt")
    MockAnthropic.assert_called_once_with()  # no args, no kwargs


def test_call_claude_uses_config_base_url_when_no_env_var(monkeypatch):
    """CONF-03:
    When env vars are absent but base_url kwarg is passed to call_claude(),
    anthropic.Anthropic() must be called with that base_url (config.json path)."""
    monkeypatch.delenv("ANTHROPIC_BASE_URL", raising=False)
    monkeypatch.delenv("ANTHROPIC_AUTH_TOKEN", raising=False)
    with patch("scripts.ai_provider.anthropic.Anthropic") as MockAnthropic:
        mock_client = MagicMock()
        MockAnthropic.return_value = mock_client
        mock_client.messages.create.return_value = MagicMock(
            content=[MagicMock(text="response")]
        )
        ap.call_claude("prompt", base_url="https://config.example.com")
    MockAnthropic.assert_called_once_with(base_url="https://config.example.com")
