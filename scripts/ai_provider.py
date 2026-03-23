"""AI provider abstraction — Phase 4.

Encapsulates provider selection and API calls for both Claude and OpenAI.
Business logic in generate_exercises.py calls call_ai() without knowing
which provider is active.

Provider resolution priority:
    1. AI_PROVIDER env var (if set and non-empty)
    2. ai_provider field in config dict (defaults to "anthropic")
"""
import os
import sys

import anthropic
import openai

VALID_PROVIDERS = {"anthropic", "openai"}
CLAUDE_MODEL = "claude-haiku-4-5-20251001"


def resolve_provider(config: dict) -> str:
    """Resolve active AI provider. Env var AI_PROVIDER takes priority over config."""
    provider = os.environ.get("AI_PROVIDER") or config.get("ai_provider", "anthropic")
    if provider not in VALID_PROVIDERS:
        print(
            f"ERROR: Unknown AI provider '{provider}'. Valid: {sorted(VALID_PROVIDERS)}",
            file=sys.stderr,
        )
        sys.exit(1)
    return provider


def call_claude(prompt: str, max_tokens: int = 2048) -> str:
    """Call Claude API. Returns response text. Exits 1 on API error."""
    client = anthropic.Anthropic()
    try:
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text
    except anthropic.APIError as e:
        print(f"ERROR: Claude API call failed: {e}", file=sys.stderr)
        sys.exit(1)


def call_openai(prompt: str, model: str, max_tokens: int = 2048) -> str:
    """Call OpenAI API. Returns response text. Exits 1 on any error."""
    client = openai.OpenAI()  # reads OPENAI_API_KEY from env automatically
    try:
        response = client.chat.completions.create(
            model=model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"ERROR: OpenAI API call failed: {e}", file=sys.stderr)
        sys.exit(1)


def call_ai(prompt: str, provider: str, model_config: dict, max_tokens: int = 2048) -> str:
    """Dispatch to the active AI provider.

    Args:
        prompt: The full prompt string to send.
        provider: 'anthropic' or 'openai' (already resolved by resolve_provider).
        model_config: Dict with at least 'openai_model' key for OpenAI path.
        max_tokens: Maximum tokens in response.
    """
    if provider == "openai":
        return call_openai(prompt, model=model_config["openai_model"], max_tokens=max_tokens)
    return call_claude(prompt, max_tokens=max_tokens)
