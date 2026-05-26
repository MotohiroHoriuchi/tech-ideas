"""
Compose one LINE push message from tmp/hot.json and tmp/research.json, then send.
"""
import json
import os
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).parent.parent
TMP_DIR = REPO_ROOT / "tmp"

LINE_API = "https://api.line.me/v2/bot/message/push"
MAX_TITLE_LEN = 30
TOP_N_RESEARCH = 3


def truncate(text: str, n: int) -> str:
    return text if len(text) <= n else text[:n] + "..."


def build_hot_section(articles: list[dict]) -> str:
    lines = ["📰 Hot Articles"]
    numbers = "①②③④⑤⑥⑦⑧⑨⑩"
    for i, a in enumerate(articles):
        num = numbers[i] if i < len(numbers) else f"{i+1}."
        title = truncate(a["title"], MAX_TITLE_LEN)
        lines.append(f"{num} {title} @{a['author']} 👍{a['likes']}")
        lines.append(a["url"])
    return "\n".join(lines)


def build_research_section(updates: list[dict]) -> str:
    if not updates:
        return ""
    lines = ["---", "🔍 調査更新"]
    for u in updates:
        lines.append(f"\n▶ {u['slug']}（{u['day']}日目 / {u['total_days']}日）")
        lines.append(f"クエリ: {u['query']}")
        for i, a in enumerate(u["articles"][:TOP_N_RESEARCH]):
            num = ["①", "②", "③"][i]
            title = truncate(a["title"], MAX_TITLE_LEN)
            lines.append(f"{num} {title} @{a['author']} 👍{a['likes']}")
            lines.append(a["url"])
        if len(u["articles"]) > TOP_N_RESEARCH:
            lines.append(f"全{len(u['articles'])}件 → 101_PriorReserch/{u['slug']}.md")
    return "\n".join(lines)


def send_line(token: str, user_id: str, text: str) -> None:
    resp = requests.post(
        LINE_API,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={"to": user_id, "messages": [{"type": "text", "text": text}]},
        timeout=10,
    )
    resp.raise_for_status()
    print(f"LINE sent: HTTP {resp.status_code}")


def main():
    token = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
    user_id = os.environ["LINE_USER_ID"]

    from datetime import date
    today = date.today().isoformat()

    hot_path = TMP_DIR / "hot.json"
    research_path = TMP_DIR / "research.json"

    hot_articles = json.loads(hot_path.read_text(encoding="utf-8")) if hot_path.exists() else []
    research_updates = json.loads(research_path.read_text(encoding="utf-8")) if research_path.exists() else []

    parts = [f"【Zenn Daily {today}】", ""]
    parts.append(build_hot_section(hot_articles))

    research_text = build_research_section(research_updates)
    if research_text:
        parts.append(research_text)

    message = "\n".join(parts)

    if len(message) > 5000:
        message = message[:4997] + "..."

    send_line(token, user_id, message)


if __name__ == "__main__":
    main()
