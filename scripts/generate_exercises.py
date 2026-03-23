"""AI exercise generator — Phase 3.

Reads Article Envelope JSON from stdin, calls Claude API once,
outputs full Markdown lesson to stdout.

Usage (in pipeline):
    python -m scripts.feed_article | python -m scripts.generate_exercises
"""
import json
import sys

import anthropic


MODEL = "claude-haiku-4-5-20251001"


def build_prompt(envelope: dict) -> str:
    """Build the Claude prompt from an Article Envelope dict."""
    title = envelope["title"]
    body = envelope["body"]
    return f"""You are an English learning assistant for Chinese speakers studying at B1-B2 level.

Given the article below, return a JSON object with three keys: "vocabulary", "chunks", "questions".

RULES:
- vocabulary: array of 5-8 objects. Each: word (str), part_of_speech (str), chinese_meaning (str), \
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


def call_claude(prompt: str, max_tokens: int = 2048) -> str:
    """Call Claude API. Returns response text. Exits 1 on any error."""
    client = anthropic.Anthropic()
    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text
    except Exception as e:
        print(f"ERROR: Claude API call failed: {e}", file=sys.stderr)
        sys.exit(1)


def parse_response(raw_text: str) -> dict:
    """Parse Claude JSON response. Exits 1 if malformed or incomplete."""
    text = raw_text.strip()
    # Defensive strip of accidental code fences
    if text.startswith("```"):
        text = text.lstrip("`").lstrip("json").strip().rstrip("`").strip()
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        print(f"ERROR: Claude returned invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)
    required = {"vocabulary", "chunks", "questions"}
    missing = required - set(data.keys())
    if missing:
        print(f"ERROR: Claude response missing keys: {missing}", file=sys.stderr)
        sys.exit(1)
    if len(data["vocabulary"]) < 5:
        print(
            f"ERROR: Claude returned only {len(data['vocabulary'])} vocabulary items (need 5+)",
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
        lines.append(
            f"**{item['word']}** ({item['part_of_speech']}) （{item['chinese_meaning']}）"
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


def main() -> None:
    """Entry point: read Article Envelope from stdin, output Markdown to stdout."""
    raw = sys.stdin.read()
    try:
        envelope = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON from stdin: {e}", file=sys.stderr)
        sys.exit(1)

    prompt = build_prompt(envelope)
    raw_response = call_claude(prompt)
    exercises = parse_response(raw_response)
    markdown = render_markdown(envelope, exercises)
    print(markdown)


if __name__ == "__main__":
    main()
