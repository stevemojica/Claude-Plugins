#!/usr/bin/env bash
# SessionStart hook: installs Zendesk plugins from this repo into ~/.claude/plugins/
# so they are available in Cowork (cloud) sessions.

set -e

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PLUGIN_DIR="$HOME/.claude/plugins"

for plugin in zendesk-support-analytics zendesk-wiki-suggester; do
  src="$REPO_DIR/$plugin"
  dest="$PLUGIN_DIR/$plugin"

  if [ ! -d "$src" ]; then
    echo "[install-plugins] WARNING: $src not found, skipping"
    continue
  fi

  # Skip if already installed and identical
  if [ -d "$dest" ] && diff -rq "$src/.claude-plugin" "$dest/.claude-plugin" >/dev/null 2>&1; then
    echo "[install-plugins] $plugin already installed, skipping"
    continue
  fi

  mkdir -p "$dest"
  cp -r "$src/.claude-plugin" "$dest/"
  cp -r "$src/commands" "$dest/" 2>/dev/null || true
  cp -r "$src/skills" "$dest/" 2>/dev/null || true

  # Copy .env if it exists in the repo (for Cowork sessions where global env may not be set)
  if [ -f "$src/.env" ]; then
    cp "$src/.env" "$dest/.env"
  fi

  echo "[install-plugins] Installed $plugin -> $dest"
done

echo "[install-plugins] Done"
