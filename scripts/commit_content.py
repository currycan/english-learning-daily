import subprocess
import sys
from datetime import date
from pathlib import Path

from scripts.content_utils import get_beijing_date, content_path, CONTENT_DIR


def git_commit_and_push(path: Path, today: date) -> None:
    try:
        subprocess.run(["git", "add", str(path)], check=True)
        subprocess.run(
            ["git", "commit", "-m", f"content: add {today.isoformat()}"],
            check=True,
        )
        subprocess.run(["git", "push"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"ERROR: git operation failed: {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    today = get_beijing_date()
    path = content_path(today)

    if path.exists():
        print(f"Content for {today} already exists — skipping.")
        sys.exit(0)

    CONTENT_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(f"# {today}\n\n_Content placeholder — Phase 1_\n")
    print(f"Wrote placeholder: {path}")

    git_commit_and_push(path, today)


if __name__ == "__main__":
    main()
