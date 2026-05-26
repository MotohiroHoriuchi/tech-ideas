"""
Fetch top 10 trending Zenn articles and write to 100_HotArticles/YYYY-MM-DD.md.
Outputs tmp/hot.json for notify.py.
"""
import json
import os
from datetime import date, timezone, timedelta
from pathlib import Path

import requests

JST = timezone(timedelta(hours=9))
TODAY = date.today().isoformat()

REPO_ROOT = Path(__file__).parent.parent
OUT_DIR = REPO_ROOT / "100_HotArticles"
TMP_DIR = REPO_ROOT / "tmp"
OUT_MD = OUT_DIR / f"{TODAY}.md"
OUT_JSON = TMP_DIR / "hot.json"

ZENN_API = "https://zenn.dev/api/articles"


def fetch_trending(count: int = 10) -> list[dict]:
    resp = requests.get(ZENN_API, params={"order": "trending", "count": count}, timeout=10)
    resp.raise_for_status()
    return resp.json().get("articles", [])


def build_md(articles: list[dict]) -> str:
    rows = "\n".join(
        f"| {i+1} | {a['title']} | {a['user']['username']} | {a['liked_count']} | https://zenn.dev{a['path']} |"
        for i, a in enumerate(articles)
    )
    return f"""---
date: {TODAY}
source: zenn
type: hot-articles
---

# Zenn Hot Articles - {TODAY}

| # | タイトル | 著者 | いいね | URL |
|---|---------|------|--------|-----|
{rows}
"""


def main():
    OUT_DIR.mkdir(exist_ok=True)
    TMP_DIR.mkdir(exist_ok=True)

    articles = fetch_trending()

    if not OUT_MD.exists():
        OUT_MD.write_text(build_md(articles), encoding="utf-8")
        print(f"Written: {OUT_MD}")

    payload = [
        {
            "title": a["title"],
            "author": a["user"]["username"],
            "likes": a["liked_count"],
            "url": f"https://zenn.dev{a['path']}",
        }
        for a in articles
    ]
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Written: {OUT_JSON}")


if __name__ == "__main__":
    main()
