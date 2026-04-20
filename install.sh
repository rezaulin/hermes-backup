#!/bin/bash
# Hermes One-Command Install + Profile Restore
# Usage: bash install.sh
# Works on fresh Ubuntu VPS

set -e

BACKUP_DIR="$(cd "$(dirname "$0")" && pwd)"
HERMES_DIR="$HOME/.hermes"

echo "🔧 Hermes Full Setup..."
echo ""

# ─── 1. System deps ───
echo "📦 Installing system dependencies..."
apt-get update -qq && apt-get install -y -qq python3 python3-pip python3-venv git curl ffmpeg 2>/dev/null
echo "  ✅ System deps"

# ─── 2. Clone hermes-agent ───
if [ ! -d "$HOME/hermes-agent" ]; then
    echo ""
    echo "📥 Cloning hermes-agent..."
    git clone https://github.com/anthropics/hermes-agent.git "$HOME/hermes-agent" 2>/dev/null || \
    git clone https://github.com/user/hermes-agent.git "$HOME/hermes-agent" 2>/dev/null || \
    echo "  ⚠️  Clone hermes-agent manually: git clone <repo-url> ~/hermes-agent"
    if [ -d "$HOME/hermes-agent" ]; then
        echo "  ✅ hermes-agent cloned"
    fi
else
    echo ""
    echo "  ℹ️  hermes-agent already exists, pulling latest..."
    cd "$HOME/hermes-agent" && git pull 2>/dev/null || true
    echo "  ✅ hermes-agent updated"
fi

# ─── 3. Python venv ───
if [ -d "$HOME/hermes-agent" ] && [ ! -d "$HOME/hermes-agent/venv" ]; then
    echo ""
    echo "🐍 Setting up Python venv..."
    cd "$HOME/hermes-agent"
    python3 -m venv venv
    source venv/bin/activate
    pip install -q -r requirements.txt 2>/dev/null || pip install -q openai anthropic prompt_toolkit rich pyyaml 2>/dev/null
    deactivate
    echo "  ✅ Python venv ready"
fi

# ─── 4. Create hermes dir ───
mkdir -p "$HERMES_DIR"

# ─── 5. Restore profile ───
echo ""
echo "📁 Restoring profile..."

if [ -f "$BACKUP_DIR/profiles/config.yaml" ]; then
    cp "$BACKUP_DIR/profiles/config.yaml" "$HERMES_DIR/config.yaml"
    echo "  ✅ config.yaml"
fi

if [ -f "$BACKUP_DIR/profiles/SOUL.md" ]; then
    cp "$BACKUP_DIR/profiles/SOUL.md" "$HERMES_DIR/SOUL.md"
    echo "  ✅ SOUL.md"
fi

if [ -d "$BACKUP_DIR/skills" ]; then
    mkdir -p "$HERMES_DIR/skills"
    cp -r "$BACKUP_DIR/skills/"* "$HERMES_DIR/skills/" 2>/dev/null
    echo "  ✅ skills/"
fi

if [ -d "$BACKUP_DIR/memory" ]; then
    mkdir -p "$HERMES_DIR/memories"
    cp -r "$BACKUP_DIR/memory/"* "$HERMES_DIR/memories/" 2>/dev/null
    echo "  ✅ memories/"
fi

# ─── 6. .env setup ───
if [ ! -f "$HERMES_DIR/.env" ] && [ -f "$BACKUP_DIR/profiles/.env.example" ]; then
    cp "$BACKUP_DIR/profiles/.env.example" "$HERMES_DIR/.env"
    echo "  ⚠️  .env created from template"
    echo ""
    echo "  =========================================="
    echo "  ⚠️  EDIT ~/.hermes/.env — ISI API KEY-nya!"
    echo "  =========================================="
elif [ -f "$HERMES_DIR/.env" ]; then
    echo "  ℹ️  .env already exists, skipping"
fi

# ─── 7. Symlink hermes command ───
if [ -d "$HOME/hermes-agent" ]; then
    # Try to find the entry point
    if [ -f "$HOME/hermes-agent/cli.py" ]; then
        chmod +x "$HOME/hermes-agent/cli.py" 2>/dev/null
        # Create wrapper
        cat > /usr/local/bin/hermes << 'WRAPPER'
#!/bin/bash
cd "$HOME/hermes-agent"
source venv/bin/activate 2>/dev/null
python3 cli.py "$@"
WRAPPER
        chmod +x /usr/local/bin/hermes
        echo ""
        echo "  ✅ 'hermes' command installed"
    fi
fi

# ─── Done ───
echo ""
echo "============================================"
echo "  ✅ Setup complete!"
echo "============================================"
echo ""
echo "  Next steps:"
echo "  1. Edit ~/.hermes/.env — fill in API keys"
echo "  2. Run: hermes"
echo ""
echo "  To update backup later:"
echo "  cd ~/hermes-backup && bash update.sh && git push"
echo ""
