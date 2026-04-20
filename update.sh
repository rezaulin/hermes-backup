#!/bin/bash
# Update backup from current hermes profile

BACKUP_DIR="$(cd "$(dirname "$0")" && pwd)"
HERMES_DIR="$HOME/.hermes"

echo "📦 Updating backup from current profile..."

cp "$HERMES_DIR/config.yaml" "$BACKUP_DIR/profiles/config.yaml"
cp "$HERMES_DIR/SOUL.md" "$BACKUP_DIR/profiles/SOUL.md"
rm -rf "$BACKUP_DIR/skills"
cp -r "$HERMES_DIR/skills" "$BACKUP_DIR/skills"
rm -rf "$BACKUP_DIR/memory"
mkdir -p "$BACKUP_DIR/memory"
cp -r "$HERMES_DIR/memories/"* "$BACKUP_DIR/memory/" 2>/dev/null

echo "✅ Backup updated! Now: git add -A && git commit && git push"
