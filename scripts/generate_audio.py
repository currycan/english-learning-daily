"""Audio generator using Edge TTS.

Reads today's content .md file, generates mp3 files and saves them to
website/public/audio/YYYY-MM-DD/.

Usage:
    python -m scripts.generate_audio
"""
import asyncio
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

import edge_tts

from scripts.content_utils import get_beijing_date, content_path

AUDIO_DIR = Path(__file__).parent.parent / "website" / "public" / "audio"
VOICE = "en-US-JennyNeural"


def parse_article_text(content: str) -> str:
    """Extract clean article text from markdown content."""
    match = re.search(r'## 📖 文章 / Article\s*([\s\S]*?)(?=## 📚|$)', content)
    if not match:
        return ""
    text = match.group(1).strip()
    lines = [
        line for line in text.split('\n')
        if not line.startswith('> ')
    ]
    return '\n'.join(lines).strip()


def parse_vocab_entries(content: str) -> list[dict]:
    """Extract vocabulary entries (word + example) from markdown content."""
    match = re.search(r'## 📚 词汇 / Vocabulary\s*([\s\S]*?)(?=## 🔗|$)', content)
    if not match:
        return []
    vocab_text = match.group(1)
    entries = []
    current: dict | None = None
    for line in vocab_text.split('\n'):
        m = re.match(r'\*\*(.*?)\*\*\s*\(.*?\)\s*(?:/[^/]+/)?\s*（.*?）\s*—\s*(.*)', line)
        if m:
            current = {'word': m.group(1), 'example': ''}
            entries.append(current)
        elif line.startswith('> ') and current is not None:
            current['example'] = line[2:].strip().strip('"')
    return entries


def word_to_slug(word: str) -> str:
    """Convert a word to a filesystem-safe slug."""
    return re.sub(r'[^a-z0-9]', '_', word.lower())


async def _generate_mp3(text: str, path: Path) -> None:
    """Generate a single mp3 file using Edge TTS."""
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(str(path))


async def generate_all(today: date, content: str) -> list[Path]:
    """Generate all audio files for today's content. Returns list of created paths."""
    audio_dir = AUDIO_DIR / today.isoformat()
    audio_dir.mkdir(parents=True, exist_ok=True)

    tasks = []
    paths = []

    article_text = parse_article_text(content)
    if article_text:
        path = audio_dir / "article.mp3"
        tasks.append(_generate_mp3(article_text, path))
        paths.append(path)

    for entry in parse_vocab_entries(content):
        slug = word_to_slug(entry['word'])

        word_path = audio_dir / f"vocab_{slug}.mp3"
        tasks.append(_generate_mp3(entry['word'], word_path))
        paths.append(word_path)

        if entry['example']:
            ex_path = audio_dir / f"vocab_{slug}_ex.mp3"
            tasks.append(_generate_mp3(entry['example'], ex_path))
            paths.append(ex_path)

    await asyncio.gather(*tasks)
    return paths


def git_commit_audio(paths: list[Path], date_str: str) -> None:
    """Stage and commit audio files."""
    try:
        for path in paths:
            subprocess.run(['git', 'add', str(path)], check=True)
        subprocess.run(
            ['git', 'commit', '-m', f'content: add audio {date_str}'],
            check=True,
        )
        subprocess.run(['git', 'push'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"ERROR: git operation failed: {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    """Entry point: generate audio for today's content and commit."""
    today = get_beijing_date()
    content_file = content_path(today)

    if not content_file.exists():
        print(f"ERROR: Content file {content_file} not found", file=sys.stderr)
        sys.exit(1)

    audio_dir = AUDIO_DIR / today.isoformat()
    if (audio_dir / 'article.mp3').exists():
        print(f"Audio for {today} already exists — skipping.", file=sys.stderr)
        sys.exit(0)

    content = content_file.read_text()
    paths = asyncio.run(generate_all(today, content))

    if not paths:
        print("ERROR: No audio files generated", file=sys.stderr)
        sys.exit(1)

    git_commit_audio(paths, today.isoformat())


if __name__ == "__main__":
    main()
