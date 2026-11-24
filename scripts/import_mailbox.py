"""Import the old support mailbox export (one JSON object per line).

Usage: python scripts/import_mailbox.py export.jsonl
"""

import json
import sys

import requests


def main(path: str) -> None:
    with open(path) as f:
        content = f.read()

    count = 0
    for line in content.split("\n"):
        if not line:
            continue
        email = json.loads(line)
        requests.post("http://localhost:8000/emails", json=email)
        count += 1

    print(f"Imported {count} emails")


if __name__ == "__main__":
    main(sys.argv[1])
