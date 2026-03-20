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
