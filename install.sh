#!/bin/bash
# Hermes Profile Restore Script
# Usage: bash install.sh

set -e

HERMES_DIR="$HOME/.hermes"
BACKUP_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "🔧 Restoring Hermes profile..."

# Create hermes dir if not exists
mkdir -p "$HERMES_DIR"

# Copy config
if [ -f "$BACKUP_DIR/profiles/config.yaml" ]; then
    cp "$BACKUP_DIR/profiles/config.yaml" "$HERMES_DIR/config.yaml"
    echo "  ✅ config.yaml"
fi

# Copy SOUL.md
if [ -f "$BACKUP_DIR/profiles/SOUL.md" ]; then
    cp "$BACKUP_DIR/profiles/SOUL.md" "$HERMES_DIR/SOUL.md"
    echo "  ✅ SOUL.md"
fi

# Copy skills
if [ -d "$BACKUP_DIR/skills" ]; then
    mkdir -p "$HERMES_DIR/skills"
    cp -r "$BACKUP_DIR/skills/"* "$HERMES_DIR/skills/" 2>/dev/null
    echo "  ✅ skills/"
fi

# Copy memories
if [ -d "$BACKUP_DIR/memory" ]; then
    mkdir -p "$HERMES_DIR/memories"
    cp -r "$BACKUP_DIR/memory/"* "$HERMES_DIR/memories/" 2>/dev/null
    echo "  ✅ memories/"
fi

# Create .env if not exists
if [ ! -f "$HERMES_DIR/.env" ] && [ -f "$BACKUP_DIR/profiles/.env.example" ]; then
    cp "$BACKUP_DIR/profiles/.env.example" "$HERMES_DIR/.env"
    echo "  ⚠️  .env created from template — ISI API KEY-nya!"
elif [ -f "$HERMES_DIR/.env" ]; then
    echo "  ℹ️  .env sudah ada, skip"
fi

echo ""
echo "✅ Profile restored! Jalankan: hermes"
