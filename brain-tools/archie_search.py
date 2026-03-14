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
    parser.add_argument("query")
    parser.add_argument("--top-k", type=int, default=5)
    args = parser.parse_args()

    api_url, api_key = load_config()
    req = urllib.request.Request(
        f"{api_url}/search",
        data=json.dumps({"query": args.query, "top_k": args.top_k, "tags": []}).encode(),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        body = json.loads(resp.read().decode())
    print(json.dumps(body, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
