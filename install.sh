#!/bin/bash
# Install script for Atomic SRE
set -e

echo "🤖 Installing Atomic SRE..."

# Ensure python3 is installed
if ! command -v python3 &>/dev/null; then
    echo "❌ Error: Python 3 is required but not found."
    exit 1
fi

# Check for uv package manager, install if missing
if ! command -v uv &>/dev/null; then
    echo "📦 installing uv package manager..."
    curl -sSf https://astral.sh/uv/install.sh | sh
    # Load uv environment path
    if [ -f "$HOME/.local/bin/env" ]; then
        source "$HOME/.local/bin/env"
    elif [ -f "$HOME/.cargo/env" ]; then
        source "$HOME/.cargo/env"
    fi
    export PATH="$HOME/.local/bin:$PATH"
fi

# Clone or pull latest repository
if [ ! -d "Atomic-SRE" ]; then
    echo "📥 Cloning Atomic-SRE repository..."
    git clone https://github.com/DsThakurRawat/Atomic-SRE.git
    cd Atomic-SRE
else
    echo "🔄 Updating existing Atomic-SRE repository..."
    cd Atomic-SRE
    git pull origin main
fi

# Synchronize dependencies
echo "⚡ Syncing dependencies with uv..."
uv sync

echo "✅ Atomic SRE installed successfully!"
echo ""
echo "To launch the guided CLI deployment shell, run:"
echo "  cd $(pwd) && uv run atomic-sre"
echo ""
