"""Tests for scripts.generate_audio parsing functions."""
import copy
import pytest
from scripts.generate_audio import parse_article_text, parse_vocab_entries, word_to_slug

SAMPLE_CONTENT = """\
## 📖 文章 / Article

Scientists have discovered a new species of deep-sea fish near the Pacific Ocean floor.
The creature, nicknamed the "ghost fish", lives at depths of over 3,000 meters.

> Source: https://example.com/article

## 📚 词汇 / Vocabulary

**species** (noun) /ˈspiːʃiːz/ （物种）— a group of living things that can breed together
> "Scientists have discovered a new species of deep-sea fish near the Pacific Ocean floor."

**creature** (noun) （生物）— a living thing, especially an animal
> "The creature, nicknamed the 'ghost fish', lives at depths of over 3,000 meters."

**depth** (noun) /dɛpθ/ （深度）— the distance from the top surface to the bottom
> "lives at depths of over 3,000 meters"

## 🔗 表达 / Chunking Expressions

**deep-sea** （深海的）
Used to describe things found in very deep parts of the ocean.
- Deep-sea creatures often lack eyes.
- The research team specialised in deep-sea exploration.

## ❓ 理解 / Comprehension

**Q: What is the nickname of the newly discovered fish?**
**A (EN):** The fish is nicknamed the "ghost fish".
**A (中):** 这种鱼被昵称为"幽灵鱼"。
"""


class TestParseArticleText:
    def test_extracts_article_paragraphs(self):
        result = parse_article_text(SAMPLE_CONTENT)
        assert "Scientists have discovered" in result
        assert "ghost fish" in result

    def test_excludes_source_line(self):
        result = parse_article_text(SAMPLE_CONTENT)
        assert "Source:" not in result
        assert "https://example.com" not in result

    def test_returns_empty_when_no_article_section(self):
        result = parse_article_text("## 📚 词汇 / Vocabulary\n\nsome content")
        assert result == ""

    def test_returns_empty_on_empty_input(self):
        result = parse_article_text("")
        assert result == ""


class TestParseVocabEntries:
    def test_extracts_word_and_example(self):
        entries = parse_vocab_entries(SAMPLE_CONTENT)
        assert len(entries) == 3
        assert entries[0]['word'] == 'species'
        assert "Scientists have discovered" in entries[0]['example']

    def test_handles_entry_without_ipa(self):
        entries = parse_vocab_entries(SAMPLE_CONTENT)
        creature = next(e for e in entries if e['word'] == 'creature')
        assert creature['word'] == 'creature'
        assert "ghost fish" in creature['example']

    def test_handles_entry_with_ipa(self):
        entries = parse_vocab_entries(SAMPLE_CONTENT)
        species = next(e for e in entries if e['word'] == 'species')
        assert species['word'] == 'species'

    def test_returns_empty_when_no_vocab_section(self):
        result = parse_vocab_entries("## 📖 文章 / Article\n\nsome content")
        assert result == []

    def test_returns_empty_on_empty_input(self):
        result = parse_vocab_entries("")
        assert result == []


class TestWordToSlug:
    def test_lowercase(self):
        assert word_to_slug("Trend") == "trend"

    def test_replaces_non_alphanumeric(self):
        assert word_to_slug("break-even") == "break_even"

    def test_handles_spaces(self):
        assert word_to_slug("look up") == "look_up"

    def test_simple_word(self):
        assert word_to_slug("species") == "species"


import asyncio
from datetime import date
from pathlib import Path
from unittest.mock import patch, AsyncMock, MagicMock, call
from scripts.generate_audio import generate_all, git_commit_audio, word_to_slug, AUDIO_DIR


class TestGenerateAll:
    """Tests for generate_all() — mocks edge_tts.Communicate to avoid network calls."""

    def test_creates_article_and_vocab_audio_paths(self, tmp_path):
        """generate_all returns paths for article + vocab + examples."""
        content = SAMPLE_CONTENT
        today = date(2026, 3, 26)

        with patch("scripts.generate_audio.AUDIO_DIR", tmp_path), \
             patch("scripts.generate_audio._generate_mp3", new_callable=AsyncMock) as mock_mp3:
            paths = asyncio.run(generate_all(today, content))

        assert len(paths) > 0
        path_names = [p.name for p in paths]
        assert "article.mp3" in path_names
        assert any(n.startswith("vocab_") and not n.endswith("_ex.mp3") for n in path_names)
        assert any(n.endswith("_ex.mp3") for n in path_names)

    def test_warns_when_no_article_text(self, tmp_path, capsys):
        """generate_all prints warning to stderr when article section is missing."""
        content = "## 📚 词汇 / Vocabulary\n\n**word** (noun) （释义）— def\n> \"example\"\n"
        today = date(2026, 3, 26)

        with patch("scripts.generate_audio.AUDIO_DIR", tmp_path), \
             patch("scripts.generate_audio._generate_mp3", new_callable=AsyncMock):
            paths = asyncio.run(generate_all(today, content))

        captured = capsys.readouterr()
        assert "WARNING" in captured.err

    def test_skips_example_audio_when_no_example(self, tmp_path):
        """generate_all does not create _ex.mp3 when vocab entry has no example."""
        content = """\
## 📖 文章 / Article

Some article text here.

## 📚 词汇 / Vocabulary

**trend** (noun) /trɛnd/ （趋势）— a direction
"""
        today = date(2026, 3, 26)

        with patch("scripts.generate_audio.AUDIO_DIR", tmp_path), \
             patch("scripts.generate_audio._generate_mp3", new_callable=AsyncMock):
            paths = asyncio.run(generate_all(today, content))

        path_names = [p.name for p in paths]
        assert not any(n.endswith("_ex.mp3") for n in path_names)


class TestGitCommitAudio:
    """Tests for git_commit_audio() — mocks subprocess.run."""

    def test_adds_and_commits_all_paths(self):
        """git_commit_audio calls git add for each path and then commits."""
        paths = [Path("/repo/audio/article.mp3"), Path("/repo/audio/vocab_trend.mp3")]
        date_str = "2026-03-26"

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            git_commit_audio(paths, date_str)

        calls = mock_run.call_args_list
        # Should have: N git add + 1 git commit + 1 git push
        add_calls = [c for c in calls if c.args[0][0:2] == ['git', 'add']]
        commit_calls = [c for c in calls if c.args[0][0:2] == ['git', 'commit']]
        push_calls = [c for c in calls if c.args[0] == ['git', 'push']]

        assert len(add_calls) == len(paths)
        assert len(commit_calls) == 1
        assert f"audio {date_str}" in commit_calls[0].args[0][-1]
        assert len(push_calls) == 1

    def test_exits_on_subprocess_failure(self):
        """git_commit_audio calls sys.exit(1) when subprocess raises CalledProcessError."""
        import subprocess
        paths = [Path("/repo/audio/article.mp3")]

        with patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "git")), \
             pytest.raises(SystemExit) as exc_info:
            git_commit_audio(paths, "2026-03-26")

        assert exc_info.value.code == 1
