# API メモ

## Zenn API

公式ドキュメントは存在しないが、フロントエンドが使っている以下のエンドポイントを利用する。

### トレンド記事取得

```
GET https://zenn.dev/api/articles?order=trending&count=10
```

レスポンス例:
```json
{
  "articles": [
    {
      "id": 123456,
      "title": "記事タイトル",
      "slug": "article-slug",
      "path": "/username/articles/article-slug",
      "emoji": "🦀",
      "liked_count": 42,
      "comments_count": 3,
      "published_at": "2026-05-25T10:00:00.000+09:00",
      "user": {
        "username": "username",
        "name": "表示名"
      },
      "topics": [{"name": "rust"}, {"name": "async"}]
    }
  ]
}
```

URL の組み立て: `https://zenn.dev` + `path`

### 記事検索

```
GET https://zenn.dev/api/search?q={query}&order=relevant&source=articles&count=10
```

レスポンス構造は上記と同じ `articles` 配列。

---

## LINE Messaging API

### Push Message

```
POST https://api.line.me/v2/bot/message/push
Authorization: Bearer {LINE_CHANNEL_ACCESS_TOKEN}
Content-Type: application/json

{
  "to": "{LINE_USER_ID}",
  "messages": [
    {
      "type": "text",
      "text": "メッセージ本文（最大5000文字）"
    }
  ]
}
```

### User ID の取得

ボットを友達追加した後、Webhook で受け取るか以下で取得:

```
GET https://api.line.me/v2/bot/followers/ids
Authorization: Bearer {LINE_CHANNEL_ACCESS_TOKEN}
```

レスポンス:
```json
{
  "userIds": ["Uxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"],
  "next": null
}
```

### 無料枠

- 月 200 通まで無料（2025年以降の仕様）
- 超過分は従量課金（このパイプラインでは月 30 通程度なので問題なし）
