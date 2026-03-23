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


def test_call_openai_exits_on_error():
    with patch("scripts.ai_provider.openai.OpenAI") as MockOpenAI:
        mock_client = MagicMock()
        MockOpenAI.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("err")
        with pytest.raises(SystemExit) as exc_info:
            ap.call_openai("test prompt", model="gpt-4o-mini")
    assert exc_info.value.code == 1


# ---------------------------------------------------------------------------
# call_claude tests
# ---------------------------------------------------------------------------


def test_call_claude_exits_on_api_error():
    with patch("scripts.ai_provider.anthropic.Anthropic") as MockAnthropic:
        mock_client = MagicMock()
        MockAnthropic.return_value = mock_client
        mock_client.messages.create.side_effect = anthropic.APIError(
            message="err", request=MagicMock(), body=None
        )
        with pytest.raises(SystemExit) as exc_info:
            ap.call_claude("prompt")
    assert exc_info.value.code == 1


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
