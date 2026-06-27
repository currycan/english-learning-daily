"""AI provider — Gemini only.

Single provider: call_gemini() wraps the google-genai SDK.
API key resolution: GEMINI_API_KEY env var > api_key parameter > empty string.

Transient API errors (503 UNAVAILABLE, 429 rate limit, 500, timeouts) are
retried with exponential backoff before giving up — the scheduled jobs were
hard-failing on momentary Gemini overload ("high demand") with no retry.
"""
import os
import sys
import time

from google import genai

GEMINI_MODEL = "gemini-2.5-flash-lite"

# Retry policy for transient failures.
MAX_ATTEMPTS = 4
BASE_DELAY_SECONDS = 2.0

# Substrings that mark a retryable (transient) server-side condition.
_TRANSIENT_MARKERS = (
    "503",
    "unavailable",
    "429",
    "resource_exhausted",
    "rate limit",
    "overloaded",
    "high demand",
    "500",
    "internal error",
    "deadline",
    "timeout",
    "temporarily",
)


class ProviderError(Exception):
    """Raised when an AI provider API call fails."""


def _is_transient(err: Exception) -> bool:
    msg = str(err).lower()
    return any(marker in msg for marker in _TRANSIENT_MARKERS)


def call_gemini(
    prompt: str,
    max_tokens: int = 2048,
    model: str | None = None,
    api_key: str | None = None,
) -> str:
    """Call Gemini API. Returns response text. Raises ProviderError on failure.

    Retries transient errors with exponential backoff; non-transient errors
    (bad key, invalid request) fail fast.
    """
    key = os.environ.get("GEMINI_API_KEY") or api_key or ""
    effective_model = model or GEMINI_MODEL
    print(f"INFO: Gemini model: {effective_model}", file=sys.stderr)
    client = genai.Client(api_key=key)

    last_error: Exception | None = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = client.models.generate_content(
                model=effective_model,
                contents=prompt,
            )
            text = response.text
            if not text or not text.strip():
                raise ProviderError("Gemini returned an empty response")
            return text
        except ProviderError:
            # Empty response — surface immediately, no point retrying the wrap.
            raise
        except Exception as e:  # noqa: BLE001 — SDK raises a variety of error types
            last_error = e
            if _is_transient(e) and attempt < MAX_ATTEMPTS:
                delay = BASE_DELAY_SECONDS * (2 ** (attempt - 1))
                print(
                    f"WARN: transient Gemini error "
                    f"(attempt {attempt}/{MAX_ATTEMPTS}), retrying in {delay:.0f}s: {e}",
                    file=sys.stderr,
                )
                time.sleep(delay)
                continue
            raise ProviderError(f"Gemini API call failed: {e}") from e

    # Exhausted retries on transient errors.
    raise ProviderError(
        f"Gemini API call failed after {MAX_ATTEMPTS} attempts: {last_error}"
    )
