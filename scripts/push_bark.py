import json
import os
import sys

import requests


BARK_BASE_URL = "https://api.day.app"


def send_to_bark(payload: dict, token: str) -> None:
    if not token:
        print("ERROR: BARK_TOKEN environment variable not set", file=sys.stderr)
        sys.exit(1)

    post_data = {
        "title": payload["title"],
        "body": payload["body"],
    }
    if payload.get("url") is not None:
        post_data["url"] = payload["url"]

    url = f"{BARK_BASE_URL}/{token}"
    response = requests.post(url, json=post_data, timeout=10)

    if response.status_code < 200 or response.status_code >= 300:
        print(f"ERROR: Bark API returned {response.status_code}: {response.text}", file=sys.stderr)
        sys.exit(1)


def main(push_type: str = "morning") -> None:
    token = os.environ.get("BARK_TOKEN", "")
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON from stdin: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"[{push_type}] Sending Bark notification: {payload['title']}")
    send_to_bark(payload, token=token)
    print(f"[{push_type}] Sent successfully.")


if __name__ == "__main__":
    push_type = sys.argv[1] if len(sys.argv) > 1 else "morning"
    main(push_type)
