---
title: "GitHub Actions + Zenn API + LINE で作る個人ナレッジ自動収集パイプライン"
emoji: 🤖
type: tech
topics: [githubactions, zenn, line, python, obsidian]
published: false
---

## TL;DR

- 毎朝 Zenn トレンドを自動取得して Obsidian に保存 & LINE 通知
- 自分のアイデアファイルに書いたキーワードで関連記事を 7 日間追跡調査
- 全て無料（GitHub Actions / Zenn 公開 API / LINE Messaging API 無料枠）
- `git pull` するだけで Obsidian に同期される

## 動機

Zenn のトレンドを毎日チェックしたいけど見に行くのが面倒。  
自分がアイデアを書いたとき、関連する先行記事を自動で集めてほしい。  
そして全部 Obsidian に溜めておきたい。

## アーキテクチャ

（system.pu の図を貼る）

3 本のスクリプトがパイプラインを構成する。

| スクリプト | 役割 | 出力 |
|-----------|------|------|
| `hot_articles.py` | Zenn トレンド取得・md 生成 | `100_HotArticles/YYYY-MM-DD.md`, `tmp/hot.json` |
| `idea_research.py` | アイデア調査・md 追記 | `101_PriorReserch/<slug>.md`, `tmp/research.json` |
| `notify.py` | LINE 1 通に合成して送信 | — |

各スクリプトは `tmp/*.json` を中間ファイルとして受け渡す。  
→ テストしやすく、LINE 送信だけ切り離して再実行できる。

## 工夫したポイント

### topics → title フォールバックの検索クエリ設計

アイデアファイルに `topics: [rust, async]` があればそれを検索キーワードに使う。  
なければ `title` の先頭 50 文字にフォールバック。  
Zenn の検索はタグ検索と相性が良いため、topics があるほど精度が上がる。

### 7 日間の調査期間トラッキング

`101_PriorReserch/<slug>.md` の frontmatter に `research_start` を記録し、  
7 日経過したアイデアはスキップ。新しい `## YYYY-MM-DD` セクションを日次で追記していく。

### LINE 1 通/日設計

無料枠（200 通/月）を温存するため、Hot Articles と調査更新を 1 通に合成。  
調査更新がない日は Hot Articles セクションのみ送信。

### git push で Obsidian 同期

GitHub Actions が `git commit & push` → ユーザーが `git pull` するだけで  
Obsidian に最新 md が届く。iCloud 経由のリアルタイム同期は不要。

## セットアップ手順

### 1. リポジトリの準備

```bash
cd ~/path/to/tech-ideas
git init
git add .gitignore CLAUDE.md .design scripts .github 100_HotArticles 002_Idea 101_PriorReserch
git commit -m "init: zenn auto-research pipeline"
gh repo create tech-ideas --private --source=. --push
```

### 2. LINE Messaging API の設定

1. [LINE Developers Console](https://developers.line.biz/) でプロバイダーを作成
2. Messaging API チャネルを作成
3. 「チャネルアクセストークン（長期）」を発行
4. スマホでボットを友達追加
5. 自分の User ID を取得（`GET https://api.line.me/v2/bot/followers/ids` で取得可）

### 3. GitHub Secrets の登録

| Secret 名 | 値 |
|-----------|---|
| `LINE_CHANNEL_ACCESS_TOKEN` | LINE チャネルアクセストークン |
| `LINE_USER_ID` | 自分の LINE User ID（`Uxxxxxxxx...`） |

### 4. アイデアファイルの書き方

`002_Idea/` に以下の形式でファイルを作る：

```markdown
---
title: "Rust で非同期処理を学ぶ"
topics: [rust, async, tokio]
---

アイデアの内容...
```

ファイル名は `00001_rust-async.md` のように 0 埋め 5 桁プレフィックスをつける。  
作成した翌日から 7 日間、毎朝関連記事が `101_PriorReserch/00001_rust-async.md` に追記される。

## コスト

| 項目 | 使用量 | 無料枠 |
|------|--------|--------|
| GitHub Actions | ~1 run/日 × 2 min ≈ 60 min/月 | 2000 min/月（private） |
| LINE Messaging API | 1 通/日 × 30 日 = 30 通/月 | 200 通/月 |
| Zenn API | 公開 API | 制限なし |
