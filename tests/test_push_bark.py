import json
import sys
from unittest.mock import patch, MagicMock

import pytest

from scripts.push_bark import send_to_bark, main


VALID_PAYLOAD = {"title": "Test title", "body": "Test body", "url": None}


def test_send_to_bark_calls_correct_url():
    with patch("scripts.push_bark.requests.post") as mock_post:
        mock_post.return_value = MagicMock(status_code=200, text="ok")
        send_to_bark(VALID_PAYLOAD, token="testtoken")
        called_url = mock_post.call_args[0][0]
        assert "testtoken" in called_url

def test_send_to_bark_omits_url_when_none():
    with patch("scripts.push_bark.requests.post") as mock_post:
        mock_post.return_value = MagicMock(status_code=200, text="ok")
        send_to_bark(VALID_PAYLOAD, token="testtoken")
        post_data = mock_post.call_args[1].get("json", {})
        assert "url" not in post_data

def test_send_to_bark_exits_nonzero_on_api_error():
    with patch("scripts.push_bark.requests.post") as mock_post:
        mock_post.return_value = MagicMock(status_code=400, text="bad request")
        with pytest.raises(SystemExit) as exc:
            send_to_bark(VALID_PAYLOAD, token="testtoken")
        assert exc.value.code != 0

def test_send_to_bark_exits_nonzero_on_missing_token():
    with pytest.raises(SystemExit) as exc:
        send_to_bark(VALID_PAYLOAD, token="")
    assert exc.value.code != 0

def test_send_to_bark_includes_url_when_provided():
    payload_with_url = {"title": "Test", "body": "Body", "url": "https://example.com"}
    with patch("scripts.push_bark.requests.post") as mock_post:
        mock_post.return_value = MagicMock(status_code=200, text="ok")
        send_to_bark(payload_with_url, token="testtoken")
        post_data = mock_post.call_args[1].get("json", {})
        assert post_data.get("url") == "https://example.com"

def test_main_reads_stdin_and_sends(monkeypatch):
    import io
    payload_json = json.dumps({"title": "T", "body": "B", "url": None})
    monkeypatch.setenv("BARK_TOKEN", "tok123")
    with patch("scripts.push_bark.send_to_bark") as mock_send:
        with patch("sys.stdin", io.StringIO(payload_json)):
            main("morning")
        mock_send.assert_called_once()
        call_args = mock_send.call_args
        assert call_args[1]["token"] == "tok123" or call_args[0][1] == "tok123"

def test_main_uses_bark_token_env_var(monkeypatch):
    import io
    monkeypatch.setenv("BARK_TOKEN", "mytoken")
    payload_json = json.dumps({"title": "T", "body": "B", "url": None})
    with patch("scripts.push_bark.send_to_bark") as mock_send:
        with patch("sys.stdin", io.StringIO(payload_json)):
            main()
        _, kwargs = mock_send.call_args
        token_used = kwargs.get("token") or mock_send.call_args[0][1]
        assert token_used == "mytoken"
