# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository overview

This is an Obsidian vault for technical idea management, combined with a Zenn publication project. The vault is synced via iCloud.

## Directory layout

| Path | Purpose |
|------|---------|
| `001_Zenn/` | Zenn publication project (has its own `.git` repo) |
| `002_Idea/` | Freeform idea notes in Markdown |
| `100_HotArticles/` | Daily Zenn trending article digests (YAML frontmatter + table) |
| `101_PriorReserch/` | Research notes linked to ideas in `002_Idea/` |

## Zenn article workflow (`001_Zenn/`)

```bash
cd 001_Zenn
npx zenn new:article          # scaffold a new article
npx zenn preview              # local preview at http://localhost:8000
```

Publishing is done by pushing to GitHub (Zenn syncs from the repo). There is no build or test step.

### Article frontmatter

```yaml
---
title: ""
emoji: ""
type: idea          # "idea" or "tech"
topics: []
published: true
---
```

## Markdown conventions for `100_HotArticles/` and `101_PriorReserch/`

Files use YAML frontmatter followed by a Markdown table. Example shape for `100_HotArticles/YYYY-MM-DD.md`:

```yaml
---
date: YYYY-MM-DD
source: zenn
type: hot-articles
---
```

`101_PriorReserch/` files additionally carry an `idea` field pointing to the source file in `002_Idea/` and use an Obsidian wikilink (`[[002_Idea/filename.md]]`) for cross-referencing.

## Automation pipeline

### Running locally

```bash
pip install requests pyyaml

python scripts/hot_articles.py   # → 100_HotArticles/YYYY-MM-DD.md + tmp/hot.json
python scripts/idea_research.py  # → 101_PriorReserch/<slug>.md + tmp/research.json

LINE_CHANNEL_ACCESS_TOKEN=xxx LINE_USER_ID=xxx python scripts/notify.py
```

### GitHub Actions

`.github/workflows/daily.yml` — runs at 10:00 JST via `cron: '0 1 * * *'`.  
Requires two repository secrets: `LINE_CHANNEL_ACCESS_TOKEN`, `LINE_USER_ID`.  
After scripts run, commits `100_HotArticles/` and `101_PriorReserch/` changes and pushes.

### Idea file naming

Files in `002_Idea/` must follow `00001_<slug>.md` (zero-padded 5-digit prefix).  
The corresponding research file is `101_PriorReserch/00001_<slug>.md`.

```yaml
# frontmatter in 002_Idea files
title: "アイデアタイトル"
topics: [keyword1, keyword2]   # used as Zenn search query; falls back to title[:50]
```

### Design docs

`.design/` stores architecture documents:
- `system.pu` — PlantUML system diagram
- `overview.md` — design doc / Zenn article draft
- `api-notes.md` — Zenn API and LINE API reference

## Recurring automation context

The owner is building a GitHub Actions pipeline that:
1. Fetches the top 10 Zenn trending articles daily → writes `100_HotArticles/YYYY-MM-DD.md`
2. Scans `002_Idea/` for recent idea files → searches Zenn for related articles → writes `101_PriorReserch/` (runs daily for ~7 days per idea)
3. Sends results via LINE Messaging API (push message to owner's user ID)

Secrets used: `LINE_CHANNEL_ACCESS_TOKEN`, `LINE_USER_ID`.

## AI agent pattern used in this project

The articles and automation scripts follow an "AI-as-hub" architecture: Bash scripts handle only file I/O and service wiring; all judgment, format conversion, and error handling is delegated to an AI agent via CLI (`claude --print`, `agy`, etc.). Prompts live in separate `.txt` template files; scripts substitute `{{PLACEHOLDER}}` variables before invoking the AI. This keeps AI models swappable by changing only the CLI command name.
