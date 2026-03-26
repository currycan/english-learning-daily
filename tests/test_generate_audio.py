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
