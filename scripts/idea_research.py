"""
Scan 002_Idea/*.md, search Zenn for related articles, append daily section to
101_PriorReserch/<slug>.md (for 7 days from research_start).
Outputs tmp/research.json for notify.py.
"""
import json
import re
from datetime import date, timedelta
from pathlib import Path

import requests
import yaml

TODAY = date.today().isoformat()
REPO_ROOT = Path(__file__).parent.parent
IDEA_DIR = REPO_ROOT / "002_Idea"
RESEARCH_DIR = REPO_ROOT / "101_PriorReserch"
TMP_DIR = REPO_ROOT / "tmp"
OUT_JSON = TMP_DIR / "research.json"

ZENN_SEARCH = "https://zenn.dev/api/search"
RESEARCH_DAYS = 7
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---", re.DOTALL)


def parse_frontmatter(text: str) -> dict:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    try:
        return yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        return {}


def build_query(fm: dict, filename: str) -> str:
    topics = fm.get("topics")
    if topics and isinstance(topics, list) and topics:
        return str(topics[0])
    title = fm.get("title", "")
    return str(title)[:50] if title else filename


def search_zenn(query: str, count: int = 10) -> list[dict]:
    resp = requests.get(
        ZENN_SEARCH,
        params={"q": query, "order": "relevant", "source": "articles", "count": count},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json().get("articles", [])


def build_research_header(idea_file: str, title: str, research_start: str) -> str:
    return f"""---
idea: 002_Idea/{idea_file}
research_start: {research_start}
last_updated: {TODAY}
---

# 関連記事: {title}

[[002_Idea/{idea_file}]]
"""


def build_day_section(articles: list[dict]) -> str:
    rows = "\n".join(
        f"| {i+1} | {a['title']} | {a['user']['username']} | {a['liked_count']} | https://zenn.dev{a['path']} |"
        for i, a in enumerate(articles)
    )
    return f"""
## {TODAY}

| # | タイトル | 著者 | いいね | URL |
|---|---------|------|--------|-----|
{rows}
"""


def process_idea(idea_path: Path) -> dict | None:
    text = idea_path.read_text(encoding="utf-8")
    fm = parse_frontmatter(text)
    slug = idea_path.stem
    res_path = RESEARCH_DIR / f"{slug}.md"

    if res_path.exists():
        res_fm = parse_frontmatter(res_path.read_text(encoding="utf-8"))
        research_start = str(res_fm.get("research_start", TODAY))
        start_date = date.fromisoformat(research_start)
        if (date.today() - start_date).days >= RESEARCH_DAYS:
            return None
    else:
        research_start = TODAY

    query = build_query(fm, slug)
    articles = search_zenn(query)
    if not articles:
        title_query = str(fm.get("title", ""))[:50] or slug
        if title_query != query:
            query = title_query
            articles = search_zenn(query)
    if not articles:
        return None

    title = str(fm.get("title", slug))

    if not res_path.exists():
        res_path.write_text(
            build_research_header(idea_path.name, title, research_start) + build_day_section(articles),
            encoding="utf-8",
        )
    else:
        existing = res_path.read_text(encoding="utf-8")
        if f"## {TODAY}" in existing:
            return None
        updated = existing.replace(
            f"last_updated: {parse_frontmatter(existing).get('last_updated', research_start)}",
            f"last_updated: {TODAY}",
        )
        res_path.write_text(updated + build_day_section(articles), encoding="utf-8")

    start_date = date.fromisoformat(research_start)
    day_num = (date.today() - start_date).days + 1

    return {
        "slug": slug,
        "title": title,
        "query": query,
        "day": day_num,
        "total_days": RESEARCH_DAYS,
        "articles": [
            {
                "title": a["title"],
                "author": a["user"]["username"],
                "likes": a["liked_count"],
                "url": f"https://zenn.dev{a['path']}",
            }
            for a in articles
        ],
    }


def main():
    RESEARCH_DIR.mkdir(exist_ok=True)
    TMP_DIR.mkdir(exist_ok=True)

    idea_files = sorted(IDEA_DIR.glob("[0-9][0-9][0-9][0-9][0-9]_*.md"))
    results = []

    for idea_path in idea_files:
        result = process_idea(idea_path)
        if result:
            results.append(result)
            print(f"Researched: {idea_path.name} (day {result['day']}/{RESEARCH_DAYS})")

    OUT_JSON.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Written: {OUT_JSON} ({len(results)} ideas updated)")


if __name__ == "__main__":
    main()
