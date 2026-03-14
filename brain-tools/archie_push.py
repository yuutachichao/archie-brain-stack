#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
import urllib.request

BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "archie_config.json"


def load_config():
    if not CONFIG_PATH.exists():
        raise FileNotFoundError("請先建立 archie_config.json（由 archie_config.json.example 複製）")
    cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    return cfg["api_url"].rstrip("/"), cfg["api_key"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--title", required=True)
    parser.add_argument("--raw-content", required=True)
    parser.add_argument("--summary", default="")
    parser.add_argument("--source-url", default="")
    parser.add_argument("--author", default="")
    parser.add_argument("--tags", nargs="*", default=[])
    parser.add_argument("--key-points", nargs="*", default=[])
    parser.add_argument("--assistant-notes", default="")
    args = parser.parse_args()

    api_url, api_key = load_config()
    payload = {
        "title": args.title,
        "source_url": args.source_url,
        "source_type": "web",
        "author": args.author,
        "language": "zh-TW",
        "raw_content": args.raw_content,
        "summary": args.summary,
        "key_points": args.key_points,
        "tags": args.tags,
        "assistant_notes": args.assistant_notes,
    }

    req = urllib.request.Request(
        f"{api_url}/ingest/article",
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        print(resp.read().decode())


if __name__ == "__main__":
    main()
