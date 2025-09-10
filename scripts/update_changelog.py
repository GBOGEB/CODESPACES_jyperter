#!/usr/bin/env python3
"""Generate requirement changelog files based on git history."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def get_git_log(req_id: str) -> list[str]:
    """Return commit summaries that mention the requirement ID."""
    try:
        result = subprocess.run(
            ["git", "log", "--pretty=format:%h %s", f"--grep={req_id}"],
            capture_output=True,
            text=True,
            check=True,
        )
    except FileNotFoundError:
        print("Error: 'git' command not found. Please ensure git is installed and available in your PATH.", file=sys.stderr)
        return []
    except subprocess.CalledProcessError:
        print("Error: Failed to run 'git log'. Make sure you are in a git repository.", file=sys.stderr)
        return []
    lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    return lines


def main(req_id: str | None = None) -> None:
    """Generate changelog files for requirements.

    If `req_id` is provided, only that requirement is processed.
    """
    index_path = Path("index.json")
    try:
        index_data = json.loads(index_path.read_text())
    except FileNotFoundError:
        print("Error: index.json not found in the current directory.", file=sys.stderr)
        return
    except json.JSONDecodeError:
        print("Error: index.json contains invalid JSON.", file=sys.stderr)
        return
    requirements = index_data["requirements"]

    if req_id:
        requirements = [r for r in requirements if r["id"] == req_id]

    out_dir = Path("docs/changelog")
    out_dir.mkdir(parents=True, exist_ok=True)

    for req in requirements:
        log_lines = get_git_log(req["id"])
        out_file = out_dir / f"{req['id']}.md"
        content = [f"# Changelog for {req['id']} - {req['title']}", ""]
        if log_lines:
            content.append("## Commits")
            content.extend(f"- {line}" for line in log_lines)
        else:
            content.append("No commits found for this requirement yet.")
        out_file.write_text("\n".join(content))


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else None
    main(arg)
