# CLAUDE.md

このファイルはリポジトリ内で Claude Code (claude.ai/code) が参照するガイダンスです。

<overview>
技術アイデア管理用の Obsidian ボルト。Zenn 執筆プロジェクトと併用する。iCloud で同期。

| パス | 用途 |
|------|------|
| `001_Zenn/` | Zenn 執筆プロジェクト（独自の `.git` リポジトリあり） |
| `002_Idea/` | 自由記述のアイデアノート |
| `100_HotArticles/` | 毎日の Zenn トレンド記事まとめ（YAMLフロントマター + テーブル） |
| `101_PriorReserch/` | `002_Idea/` のアイデアに紐づく調査ノート |
</overview>

<zenn>
コマンド:

```bash
cd 001_Zenn
npx zenn new:article          # 記事の雛形作成
npx zenn preview              # ローカルプレビュー http://localhost:8000
```

公開は GitHub へ push するだけ（Zenn がリポジトリと同期）。ビルドやテストのステップはない。

記事フロントマター:

```yaml
---
title: ""
emoji: ""
type: idea          # "idea" または "tech"
topics: []
published: true
---
```
</zenn>

<markdown-conventions>
`100_HotArticles/YYYY-MM-DD.md`:

```yaml
---
date: YYYY-MM-DD
source: zenn
type: hot-articles
---
```

`101_PriorReserch/` のファイルは `idea` フィールドで `002_Idea/` の元ファイルを指し、Obsidian のウィキリンク（`[[002_Idea/filename.md]]`）で相互参照する。
</markdown-conventions>

<automation>
ローカル実行:

```bash
pip install requests pyyaml

python scripts/hot_articles.py   # → 100_HotArticles/YYYY-MM-DD.md + tmp/hot.json
python scripts/idea_research.py  # → 101_PriorReserch/<slug>.md + tmp/research.json

LINE_CHANNEL_ACCESS_TOKEN=xxx LINE_USER_ID=xxx python scripts/notify.py
```

GitHub Actions: `.github/workflows/daily.yml` が `cron: '0 1 * * *'`（毎朝 10:00 JST）で実行。
リポジトリシークレット `LINE_CHANNEL_ACCESS_TOKEN`、`LINE_USER_ID` が必要。
実行後、`100_HotArticles/` と `101_PriorReserch/` の変更をコミット・プッシュする。

`002_Idea/` のファイル名は `00001_<slug>.md`（0埋め5桁プレフィックス）。
対応する調査ファイルは `101_PriorReserch/00001_<slug>.md`。

```yaml
# 002_Idea ファイルのフロントマター
title: "アイデアタイトル"
topics: [keyword1, keyword2]   # Zenn 検索クエリに使用。なければ title の先頭50文字にフォールバック
```

`.design/` に設計資料を格納:
- `system.pu` — PlantUML システム構成図
- `overview.md` — 設計概要 / Zenn 記事下書き
- `api-notes.md` — Zenn API・LINE API リファレンス
</automation>

<context>
GitHub Actions パイプライン:
1. 毎日 Zenn トレンド記事 10件を取得 → `100_HotArticles/YYYY-MM-DD.md` に保存
2. `002_Idea/` をスキャンして関連記事を調査 → `101_PriorReserch/` に追記（アイデアごとに7日間）
3. LINE Messaging API でオーナーに1通まとめて送信

自動化スクリプトは「AI をハブにする」アーキテクチャに従う: Bash スクリプトはファイル I/O と配線のみ担当し、判断・変換はすべて AI エージェント CLI（`claude --print`、`agy` など）に委譲する。CLI コマンド名を変えるだけでモデルを差し替えられる。
</context>
