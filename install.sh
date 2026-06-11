#!/bin/bash
# Install script for Atomic SRE
set -e

echo "Installing Atomic SRE..."

# Ensure python3 is installed
if ! command -v python3 &>/dev/null; then
    echo "Error: Python 3 is required but not found."
    exit 1
fi

# Check for uv package manager, install if missing
if ! command -v uv &>/dev/null; then
    echo "Installing uv package manager..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
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
    echo "Cloning Atomic-SRE repository..."
    git clone https://github.com/DsThakurRawat/Atomic-SRE.git
    cd Atomic-SRE
else
    echo "Updating existing Atomic-SRE repository..."
    cd Atomic-SRE
    git pull origin main
fi

# Synchronise dependencies and install CLI globally
echo "Syncing dependencies and installing CLI globally with uv..."
uv sync

# Create a fast global wrapper script instead of a slow full tool installation
echo "Creating fast global CLI wrapper..."
mkdir -p "$HOME/.local/bin"
cat << EOF > "$HOME/.local/bin/atomic-sre"
#!/bin/bash
cd "$(pwd)" && uv run atomic-sre "\$@"
EOF
chmod +x "$HOME/.local/bin/atomic-sre"

# Add ~/.local/bin to PATH permanently if it's not already there
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo "Configuring PATH to include ~/.local/bin..."
    
    # Check for bash
    if [ -f "$HOME/.bashrc" ] && ! grep -q 'export PATH="$HOME/.local/bin:$PATH"' "$HOME/.bashrc"; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
    fi
    
    # Check for zsh
    if [ -f "$HOME/.zshrc" ] && ! grep -q 'export PATH="$HOME/.local/bin:$PATH"' "$HOME/.zshrc"; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.zshrc"
    fi
    
    echo "Atomic SRE installed successfully!"
    echo ""
    echo "⚠️  IMPORTANT: To start using the tool, either restart your terminal"
    echo "or run the appropriate source command for your shell:"
    echo "  source ~/.zshrc    (if using zsh)"
    echo "  source ~/.bashrc   (if using bash)"
    echo ""
else
    echo "Atomic SRE installed successfully!"
    echo ""
    echo "You can now run it directly from anywhere:"
    echo "  atomic-sre"
    echo ""
fi
