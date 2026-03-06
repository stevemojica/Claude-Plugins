#!/bin/bash
# Setup script for Claude Token Tracker macOS menu bar app

set -e

echo "=== Claude Token Tracker — Setup ==="
echo ""

# Check macOS
if [[ "$(uname)" != "Darwin" ]]; then
    echo "Error: This app requires macOS."
    exit 1
fi

# Check Python 3
if ! command -v python3 &>/dev/null; then
    echo "Error: Python 3 is required. Install it from https://python.org or via Homebrew:"
    echo "  brew install python3"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv "$VENV_DIR"

echo "Installing dependencies..."
"$VENV_DIR/bin/pip" install --upgrade pip -q
"$VENV_DIR/bin/pip" install -r "$SCRIPT_DIR/requirements.txt" -q

echo ""
echo "Setup complete!"
echo ""
echo "To run the app:"
echo "  $SCRIPT_DIR/run.sh"
echo ""
echo "To configure your API key, either:"
echo "  1. Set ANTHROPIC_ADMIN_KEY environment variable, or"
echo "  2. Click 'Settings...' in the menu bar dropdown after launch"
echo ""
