"""AI exercise generator.

Reads Article Envelope JSON from stdin, calls AI provider once,
outputs full Markdown lesson to stdout.

Usage (in pipeline):
    python -m scripts.feed_article | python -m scripts.generate_exercises
"""
import json
import sys
from pathlib import Path

from scripts.ai_provider import call_gemini, ProviderError


def build_prompt(envelope: dict) -> str:
    """Build the AI prompt from an Article Envelope dict."""
    title = envelope["title"]
    body = envelope["body"]
    return f"""You are an English learning assistant for Chinese speakers studying at B1-B2 level.

Given the article below, return a JSON object with three keys: "vocabulary", "chunks", "questions".

RULES:
- vocabulary: array of 5-8 objects. Each: word (str), ipa (str, IPA pronunciation enclosed in /.../, e.g. /trɛnd/), \
part_of_speech (str), chinese_meaning (str), \
definition (str, plain English simpler than the word itself, B1-B2 level), \
example (str, direct verbatim quote from the article containing the word). \
Select exactly 5 to 8 vocabulary words. You MUST return at least 5.
- chunks: array of 3-5 objects. Each: chunk (str, a natural phrase or collocation from the article), \
chinese_meaning (str), english_explanation (str, usage context and register), \
examples (list of 2 strings, generated sentences showing the chunk in varied contexts).
- questions: array of 3-5 objects. Each: question (str, in English), answer_en (str), answer_zh (str). \
At least ONE question must be inferential (requiring reasoning or inference, not just recalling a stated fact).

Respond with raw JSON only. No markdown code fences, no preamble, no explanation.

Article title: {title}

Article body:
{body}"""


def parse_response(raw_text: str) -> dict:
    """Parse Claude JSON response. Exits 1 if malformed or incomplete."""
    text = raw_text.strip()
    # Defensive strip of accidental code fences
    if text.startswith("```"):
        text = text.lstrip("`").lstrip("json").strip().rstrip("`").strip()
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        print(f"ERROR: AI returned invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)
    required = {"vocabulary", "chunks", "questions"}
    missing = required - set(data.keys())
    if missing:
        print(f"ERROR: AI response missing keys: {missing}", file=sys.stderr)
        sys.exit(1)
    if len(data["vocabulary"]) < 5:
        print(
            f"ERROR: AI returned only {len(data['vocabulary'])} vocabulary items (need 5+)",
            file=sys.stderr,
        )
        sys.exit(1)
    return data


def render_markdown(envelope: dict, exercises: dict) -> str:
    """Render complete Markdown lesson from article envelope and exercises dict."""
    lines: list = []

    # Section 1: Article
    lines.append("## 📖 文章 / Article")
    lines.append("")
    lines.append(envelope["body"])
    lines.append("")
    lines.append(f"> Source: {envelope['source_url']}")
    lines.append("")

    # Section 2: Vocabulary
    lines.append("## 📚 词汇 / Vocabulary")
    lines.append("")
    for item in exercises["vocabulary"]:
        ipa_part = f" {item['ipa']}" if item.get('ipa') else ''
        lines.append(
            f"**{item['word']}** ({item['part_of_speech']}){ipa_part} （{item['chinese_meaning']}）"
            f"— {item['definition']}"
        )
        lines.append(f"> \"{item['example']}\"")
        lines.append("")

    # Section 3: Chunking Expressions
    lines.append("## 🔗 表达 / Chunking Expressions")
    lines.append("")
    for item in exercises["chunks"]:
        lines.append(f"**{item['chunk']}** （{item['chinese_meaning']}）")
        lines.append(item["english_explanation"])
        for ex in item["examples"]:
            lines.append(f"- {ex}")
        lines.append("")

    # Section 4: Comprehension
    lines.append("## ❓ 理解 / Comprehension")
    lines.append("")
    for item in exercises["questions"]:
        lines.append(f"**Q: {item['question']}**")
        lines.append(f"**A (EN):** {item['answer_en']}")
        lines.append(f"**A (中):** {item['answer_zh']}")
        lines.append("")

    return "\n".join(lines)


def _load_config() -> dict:
    """Load plan/config.json. Exits 1 on missing or malformed file."""
    config_path = Path(__file__).parent.parent / "plan" / "config.json"
    try:
        return json.loads(config_path.read_text())
    except (OSError, json.JSONDecodeError) as e:
        print(f"ERROR: Failed to load config: {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    """Entry point: read Article Envelope from stdin, output Markdown to stdout."""
    raw = sys.stdin.read()
    try:
        envelope = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON from stdin: {e}", file=sys.stderr)
        sys.exit(1)

    config = _load_config()
    prompt = build_prompt(envelope)
    try:
        raw_response = call_gemini(prompt, model=config.get("gemini_model"))
    except ProviderError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    exercises = parse_response(raw_response)
    markdown = render_markdown(envelope, exercises)
    print(markdown)


if __name__ == "__main__":
    main()
