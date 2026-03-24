import os
from unittest.mock import patch, MagicMock
import pytest
import scripts.ai_provider as ap


# ---------------------------------------------------------------------------
# Module constants tests
# ---------------------------------------------------------------------------


def test_gemini_model_constant_exists():
    assert hasattr(ap, "GEMINI_MODEL")
    assert ap.GEMINI_MODEL == "gemini-2.5-flash-lite"


def test_provider_error_is_exception():
    assert issubclass(ap.ProviderError, Exception)


# ---------------------------------------------------------------------------
# call_gemini tests
# ---------------------------------------------------------------------------


def test_call_gemini_returns_text():
    with patch("scripts.ai_provider.genai.Client") as MockClient:
        mock_client = MagicMock()
        MockClient.return_value = mock_client
        mock_client.models.generate_content.return_value = MagicMock(text="gemini response")
        result = ap.call_gemini("test prompt", api_key="fake-key")
    assert result == "gemini response"


def test_call_gemini_uses_default_model():
    with patch("scripts.ai_provider.genai.Client") as MockClient:
        mock_client = MagicMock()
        MockClient.return_value = mock_client
        mock_client.models.generate_content.return_value = MagicMock(text="ok")
        ap.call_gemini("prompt", api_key="key")
    call_kwargs = mock_client.models.generate_content.call_args
    assert call_kwargs.kwargs.get("model") == ap.GEMINI_MODEL


def test_call_gemini_uses_custom_model():
    with patch("scripts.ai_provider.genai.Client") as MockClient:
        mock_client = MagicMock()
        MockClient.return_value = mock_client
        mock_client.models.generate_content.return_value = MagicMock(text="ok")
        ap.call_gemini("prompt", model="gemini-custom", api_key="key")
    call_kwargs = mock_client.models.generate_content.call_args
    assert call_kwargs.kwargs.get("model") == "gemini-custom"


def test_call_gemini_raises_provider_error_on_exception():
    with patch("scripts.ai_provider.genai.Client") as MockClient:
        mock_client = MagicMock()
        MockClient.return_value = mock_client
        mock_client.models.generate_content.side_effect = Exception("API error")
        with pytest.raises(ap.ProviderError) as exc_info:
            ap.call_gemini("prompt", api_key="key")
    assert "Gemini API call failed" in str(exc_info.value)


def test_call_gemini_uses_env_api_key(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "env-key-123")
    with patch("scripts.ai_provider.genai.Client") as MockClient:
        mock_client = MagicMock()
        MockClient.return_value = mock_client
        mock_client.models.generate_content.return_value = MagicMock(text="ok")
        ap.call_gemini("prompt")
    MockClient.assert_called_once_with(api_key="env-key-123")


def test_call_gemini_env_key_takes_priority_over_kwarg(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "env-key")
    with patch("scripts.ai_provider.genai.Client") as MockClient:
        mock_client = MagicMock()
        MockClient.return_value = mock_client
        mock_client.models.generate_content.return_value = MagicMock(text="ok")
        ap.call_gemini("prompt", api_key="kwarg-key")
    MockClient.assert_called_once_with(api_key="env-key")


def test_call_gemini_falls_back_to_kwarg_when_no_env(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with patch("scripts.ai_provider.genai.Client") as MockClient:
        mock_client = MagicMock()
        MockClient.return_value = mock_client
        mock_client.models.generate_content.return_value = MagicMock(text="ok")
        ap.call_gemini("prompt", api_key="kwarg-key")
    MockClient.assert_called_once_with(api_key="kwarg-key")


def test_call_gemini_logs_model_to_stderr(capsys):
    with patch("scripts.ai_provider.genai.Client") as MockClient:
        mock_client = MagicMock()
        MockClient.return_value = mock_client
        mock_client.models.generate_content.return_value = MagicMock(text="ok")
        ap.call_gemini("prompt", api_key="key")
    captured = capsys.readouterr()
    assert "Gemini model" in captured.err
    assert ap.GEMINI_MODEL in captured.err


# ---------------------------------------------------------------------------
# No old provider functions should exist
# ---------------------------------------------------------------------------


def test_no_resolve_provider():
    assert not hasattr(ap, "resolve_provider")


def test_no_call_ai():
    assert not hasattr(ap, "call_ai")


def test_no_call_claude():
    assert not hasattr(ap, "call_claude")


def test_no_call_openai():
    assert not hasattr(ap, "call_openai")
