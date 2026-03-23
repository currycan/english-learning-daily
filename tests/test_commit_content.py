import subprocess
import sys
from datetime import date
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

import scripts.commit_content as cc


def test_skips_when_file_exists(tmp_path, monkeypatch):
    """If today's content file already exists, main() exits 0 without calling git."""
    today = date(2026, 3, 23)
    fake_path = tmp_path / "2026-03-23.md"
    fake_path.write_text("existing")

    monkeypatch.setattr(cc, "get_beijing_date", lambda: today)
    monkeypatch.setattr(cc, "content_path", lambda d: fake_path)

    with pytest.raises(SystemExit) as exc_info:
        cc.main()
    assert exc_info.value.code == 0


def test_writes_placeholder_when_file_absent(tmp_path, monkeypatch):
    """If today's content file does not exist, main() creates it."""
    today = date(2026, 3, 23)
    fake_path = tmp_path / "2026-03-23.md"

    monkeypatch.setattr(cc, "get_beijing_date", lambda: today)
    monkeypatch.setattr(cc, "content_path", lambda d: fake_path)
    monkeypatch.setattr(cc, "CONTENT_DIR", tmp_path)

    with patch("scripts.commit_content.git_commit_and_push") as mock_git:
        cc.main()

    assert fake_path.exists()
    assert "2026-03-23" in fake_path.read_text()
    mock_git.assert_called_once_with(fake_path, today)


def test_git_failure_exits_nonzero(monkeypatch):
    """git_commit_and_push calls sys.exit(1) when a git operation fails."""
    fake_path = Path("content/2026-03-23.md")
    today = date(2026, 3, 23)

    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = subprocess.CalledProcessError(1, "git add")
        with pytest.raises(SystemExit) as exc_info:
            cc.git_commit_and_push(fake_path, today)
    assert exc_info.value.code == 1


def test_git_commit_message_format(monkeypatch):
    """git commit message uses 'content: add YYYY-MM-DD' format."""
    fake_path = Path("content/2026-03-23.md")
    today = date(2026, 3, 23)

    calls = []
    def fake_run(cmd, check=False):
        calls.append(cmd)

    with patch("subprocess.run", side_effect=fake_run):
        cc.git_commit_and_push(fake_path, today)

    commit_cmd = next(c for c in calls if "commit" in c)
    assert "content: add 2026-03-23" in commit_cmd


def test_reads_stdin_and_writes_file(tmp_path, monkeypatch):
    """After Phase 3: main() reads Markdown from stdin and writes it to content path."""
    today = date(2026, 3, 23)
    fake_path = tmp_path / "2026-03-23.md"

    monkeypatch.setattr(cc, "get_beijing_date", lambda: today)
    monkeypatch.setattr(cc, "content_path", lambda d: fake_path)
    monkeypatch.setattr(cc, "CONTENT_DIR", tmp_path)

    stdin_content = "# Lesson\n\nSome markdown content.\n"
    monkeypatch.setattr("sys.stdin", __import__("io").StringIO(stdin_content))

    with patch("scripts.commit_content.git_commit_and_push") as mock_git:
        cc.main()

    assert fake_path.exists()
    assert fake_path.read_text() == stdin_content
    assert "placeholder" not in fake_path.read_text()
    mock_git.assert_called_once_with(fake_path, today)
