#!/bin/bash
export HOME="/Users/motohirohoriuchi"
export PATH="/usr/bin:/bin:/usr/sbin:/sbin"
REPO="/Users/motohirohoriuchi/Library/Mobile Documents/iCloud~md~obsidian/Documents/tech-ideas"
LOG="$REPO/tmp/sync.log"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] sync start" >> "$LOG"

git -C "$REPO" fetch origin >> "$LOG" 2>&1

LOCAL=$(git -C "$REPO" rev-parse @)
REMOTE=$(git -C "$REPO" rev-parse @{u})

if [ "$LOCAL" != "$REMOTE" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] changes found, merging..." >> "$LOG"
    git -C "$REPO" merge --ff-only origin/main >> "$LOG" 2>&1
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] already up to date" >> "$LOG"
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] sync done" >> "$LOG"
