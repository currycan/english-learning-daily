"""AI provider abstraction — Phase 5.

Encapsulates provider selection, API calls, and automatic fallback for both
Claude and OpenAI. Business logic in generate_exercises.py calls call_ai()
without knowing which provider is active or whether a fallback occurred.

Provider resolution priority:
    1. AI_PROVIDER env var (if set and non-empty)
    2. ai_provider field in config dict (defaults to "anthropic")

Fallback behaviour:
    If the primary provider raises ProviderError, call_ai() logs a WARNING to
    stderr, then retries exactly once with the backup provider. If the backup
    also fails, it logs an ERROR to stderr and calls sys.exit(1).
"""
import os
import sys

import anthropic
import openai

VALID_PROVIDERS = {"anthropic", "openai"}
CLAUDE_MODEL = "claude-haiku-4-5-20251001"


class ProviderError(Exception):
    """Raised when an AI provider API call fails."""


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


def call_claude(
    prompt: str,
    max_tokens: int = 2048,
    base_url: str | None = None,
    auth_token: str | None = None,
) -> str:
    """Call Claude API. Returns response text. Raises ProviderError on API error.

    base_url and auth_token enable third-party Claude-compatible endpoints.
    Priority: env vars (ANTHROPIC_BASE_URL, ANTHROPIC_AUTH_TOKEN) > kwargs > SDK defaults.
    Empty string is treated as absent (GitHub Actions returns "" for unset secrets).
    """
    # Resolve effective values: env var takes highest priority, then kwarg, then absent.
    effective_url = os.environ.get("ANTHROPIC_BASE_URL") or base_url or ""
    effective_key = os.environ.get("ANTHROPIC_AUTH_TOKEN") or auth_token or ""
    # Only pass kwargs to Anthropic() when non-empty — avoids overriding SDK defaults with None/"".
    kwargs: dict = {}
    if effective_url:
        kwargs["base_url"] = effective_url
    if effective_key:
        kwargs["api_key"] = effective_key
    client = anthropic.Anthropic(**kwargs)
    try:
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text
    except anthropic.APIError as e:
        raise ProviderError(f"Claude API call failed: {e}") from e


def call_openai(prompt: str, model: str, max_tokens: int = 2048) -> str:
    """Call OpenAI API. Returns response text. Raises ProviderError on any error.

    model_config passed to call_ai must always include 'openai_model' key so
    this function can be invoked during fallback regardless of which provider
    was primary.
    """
    client = openai.OpenAI()  # reads OPENAI_API_KEY from env automatically
    try:
        response = client.chat.completions.create(
            model=model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content
    except Exception as e:
        raise ProviderError(f"OpenAI API call failed: {e}") from e


def _backup_provider(primary: str) -> str:
    """Return the backup provider name. With exactly two providers this is deterministic."""
    return (VALID_PROVIDERS - {primary}).pop()


def _dispatch(prompt: str, provider: str, model_config: dict, max_tokens: int) -> str:
    """Route prompt to the named provider. Raises ProviderError on failure."""
    if provider == "openai":
        return call_openai(prompt, model=model_config["openai_model"], max_tokens=max_tokens)
    return call_claude(
        prompt,
        max_tokens=max_tokens,
        base_url=model_config.get("anthropic_base_url"),
        auth_token=model_config.get("anthropic_auth_token"),
    )


def call_ai(prompt: str, provider: str, model_config: dict, max_tokens: int = 2048) -> str:
    """Dispatch to the active AI provider with automatic single-retry fallback.

    Args:
        prompt: The full prompt string to send.
        provider: 'anthropic' or 'openai' (already resolved by resolve_provider).
        model_config: Dict with at least 'openai_model' key for OpenAI path.
            Must always include 'openai_model' so fallback to OpenAI works
            regardless of which provider was primary.
        max_tokens: Maximum tokens in response.

    Returns:
        Response text from the primary or backup provider.

    Raises:
        SystemExit(1): If both primary and backup providers fail.
    """
    try:
        return _dispatch(prompt, provider, model_config, max_tokens)
    except ProviderError as primary_err:
        backup = _backup_provider(provider)
        print(
            f"WARNING: Provider '{provider}' failed ({primary_err}). "
            f"Falling back to '{backup}'.",
            file=sys.stderr,
        )
        try:
            return _dispatch(prompt, backup, model_config, max_tokens)
        except ProviderError as backup_err:
            print(
                f"ERROR: Backup provider '{backup}' also failed: {backup_err}",
                file=sys.stderr,
            )
            sys.exit(1)
