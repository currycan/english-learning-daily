"""AI provider — Gemini only.

Single provider: call_gemini() wraps the google-genai SDK.
API key resolution: GEMINI_API_KEY env var > api_key parameter > empty string.
"""
import os
import sys

from google import genai

GEMINI_MODEL = "gemini-2.5-flash-lite"


class ProviderError(Exception):
    """Raised when an AI provider API call fails."""


def call_gemini(
    prompt: str,
    max_tokens: int = 2048,
    model: str | None = None,
    api_key: str | None = None,
) -> str:
    """Call Gemini API. Returns response text. Raises ProviderError on failure."""
    key = os.environ.get("GEMINI_API_KEY") or api_key or ""
    effective_model = model or GEMINI_MODEL
    print(f"INFO: Gemini model: {effective_model}", file=sys.stderr)
    client = genai.Client(api_key=key)
    try:
        response = client.models.generate_content(
            model=effective_model,
            contents=prompt,
        )
        return response.text
    except Exception as e:
        raise ProviderError(f"Gemini API call failed: {e}") from e
