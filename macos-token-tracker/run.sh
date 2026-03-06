#!/bin/bash
# Launch Claude Token Tracker menu bar app

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

if [[ ! -d "$VENV_DIR" ]]; then
    echo "Virtual environment not found. Running setup first..."
    bash "$SCRIPT_DIR/setup.sh"
fi

exec "$VENV_DIR/bin/python" "$SCRIPT_DIR/token_tracker.py"
