import json
import sys
from unittest.mock import patch, MagicMock

import pytest

import scripts.generate_exercises as ge

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

VALID_ENVELOPE = {
    "title": "Test Title",
    "body": "Test article body text. The creature has adapted to survive.",
    "source_url": "https://example.com/article",
}

VALID_EXERCISES = {
    "vocabulary": [
        {
            "word": "adapted",
            "part_of_speech": "verb",
            "chinese_meaning": "适应",
            "definition": "Changed to survive.",
            "example": "The creature has adapted to survive.",
        },
        {
            "word": "species",
            "part_of_speech": "noun",
            "chinese_meaning": "物种",
            "definition": "A group of similar animals.",
            "example": "A new species was found.",
        },
        {
            "word": "pressure",
            "part_of_speech": "noun",
            "chinese_meaning": "压力",
            "definition": "A pushing force.",
            "example": "Extreme pressure exists there.",
        },
        {
            "word": "capture",
            "part_of_speech": "verb",
            "chinese_meaning": "捕捉",
            "definition": "To catch or record.",
            "example": "Captured on camera.",
        },
        {
            "word": "expedition",
            "part_of_speech": "noun",
            "chinese_meaning": "探险",
            "definition": "A journey for discovery.",
            "example": "The expedition team left.",
        },
    ],
    "chunks": [
        {
            "chunk": "near-zero",
            "chinese_meaning": "接近零度的",
            "english_explanation": "Used in scientific contexts.",
            "examples": ["Ex one.", "Ex two."],
        },
    ],
    "questions": [
        {"question": "Why?", "answer_en": "Because.", "answer_zh": "因为。"},
    ],
}

# ---------------------------------------------------------------------------
# build_prompt tests
# ---------------------------------------------------------------------------


def test_build_prompt_contains_article():
    result = ge.build_prompt(VALID_ENVELOPE)
    assert "Test article body text." in result
    assert "vocabulary" in result
    assert "chunks" in result
    assert "questions" in result
    assert "raw JSON only" in result


def test_build_prompt_requires_b1b2():
    result = ge.build_prompt(VALID_ENVELOPE)
    assert "B1-B2" in result
    assert "simpler" in result


def test_build_prompt_inferential_instruction():
    result = ge.build_prompt(VALID_ENVELOPE)
    assert "inferential" in result or "reasoning" in result


# ---------------------------------------------------------------------------
# parse_response tests
# ---------------------------------------------------------------------------


def test_parse_response_valid():
    raw_text = json.dumps(VALID_EXERCISES)
    result = ge.parse_response(raw_text)
    assert "vocabulary" in result
    assert "chunks" in result
    assert "questions" in result


def test_parse_response_rejects_few_vocab():
    few_vocab = dict(VALID_EXERCISES)
    few_vocab = {
        "vocabulary": VALID_EXERCISES["vocabulary"][:4],  # only 4 items
        "chunks": VALID_EXERCISES["chunks"],
        "questions": VALID_EXERCISES["questions"],
    }
    raw_text = json.dumps(few_vocab)
    with pytest.raises(SystemExit) as exc_info:
        ge.parse_response(raw_text)
    assert exc_info.value.code == 1


def test_parse_response_rejects_invalid_json():
    with pytest.raises(SystemExit) as exc_info:
        ge.parse_response("not json {")
    assert exc_info.value.code == 1


def test_parse_response_strips_code_fences():
    fenced = f"```json\n{json.dumps(VALID_EXERCISES)}\n```"
    result = ge.parse_response(fenced)
    assert isinstance(result, dict)
    assert "vocabulary" in result


# ---------------------------------------------------------------------------
# render_markdown tests
# ---------------------------------------------------------------------------


def test_render_markdown_section_order():
    result = ge.render_markdown(VALID_ENVELOPE, VALID_EXERCISES)
    assert "## 📖 文章 / Article" in result
    assert "## 📚 词汇 / Vocabulary" in result
    assert "## 🔗 表达 / Chunking Expressions" in result
    assert "## ❓ 理解 / Comprehension" in result

    idx_article = result.index("## 📖 文章 / Article")
    idx_vocab = result.index("## 📚 词汇 / Vocabulary")
    idx_chunks = result.index("## 🔗 表达 / Chunking Expressions")
    idx_comprehension = result.index("## ❓ 理解 / Comprehension")
    assert idx_article < idx_vocab < idx_chunks < idx_comprehension


def test_render_markdown_source_url():
    result = ge.render_markdown(VALID_ENVELOPE, VALID_EXERCISES)
    assert "> Source: https://example.com/article" in result


def test_render_markdown_chunks():
    result = ge.render_markdown(VALID_ENVELOPE, VALID_EXERCISES)
    assert "**near-zero** （接近零度的）" in result
    assert "- Ex one." in result
    assert "- Ex two." in result


def test_render_markdown_questions():
    result = ge.render_markdown(VALID_ENVELOPE, VALID_EXERCISES)
    assert "**Q: Why?**" in result
    assert "**A (EN):** Because." in result
    assert "**A (中):** 因为。" in result


# ---------------------------------------------------------------------------
# _load_config tests
# ---------------------------------------------------------------------------


def test_load_config_returns_dict():
    """_load_config reads plan/config.json and returns a dict."""
    import scripts.generate_exercises as _ge
    config_data = {
        "morning_hour": 7,
        "gemini_model": "gemini-2.0-flash-lite",
    }
    mock_path = MagicMock()
    mock_path.read_text.return_value = json.dumps(config_data)
    with patch("scripts.generate_exercises.Path") as MockPath:
        # Path(__file__).parent.parent / "plan" / "config.json"
        MockPath.return_value.parent.parent.__truediv__.return_value.__truediv__.return_value = mock_path
        result = _ge._load_config()
    assert isinstance(result, dict)
    assert result["gemini_model"] == "gemini-2.0-flash-lite"


def test_load_config_exits_on_missing_file():
    """_load_config exits 1 if config.json is missing."""
    import scripts.generate_exercises as _ge
    mock_config_path = MagicMock()
    mock_config_path.read_text.side_effect = OSError("not found")
    with patch("scripts.generate_exercises.Path") as MockPath:
        MockPath.return_value.parent.parent.__truediv__.return_value.__truediv__.return_value = mock_config_path
        with pytest.raises(SystemExit) as exc_info:
            _ge._load_config()
    assert exc_info.value.code == 1


# ---------------------------------------------------------------------------
# main() wiring test
# ---------------------------------------------------------------------------


def test_main_calls_call_gemini(capsys):
    """main() must call call_gemini with config's gemini_model."""
    valid_envelope_json = json.dumps(VALID_ENVELOPE)
    with patch("scripts.generate_exercises._load_config") as mock_load_cfg, \
         patch("scripts.generate_exercises.call_gemini") as mock_call_gemini:
        mock_load_cfg.return_value = {"gemini_model": "gemini-2.0-flash-lite"}
        mock_call_gemini.return_value = json.dumps(VALID_EXERCISES)
        with patch("sys.stdin") as mock_stdin:
            mock_stdin.read.return_value = valid_envelope_json
            ge.main()
    mock_call_gemini.assert_called_once()
    call_kwargs = mock_call_gemini.call_args
    assert call_kwargs.kwargs.get("model") == "gemini-2.0-flash-lite"
