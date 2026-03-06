# Claude Token Usage Tracker — macOS Menu Bar

A lightweight macOS menu bar app that shows your Anthropic API token usage, rate limits, and when they reset. Works with any personal API key — no admin or org account needed.

![Python](https://img.shields.io/badge/python-3.9+-blue)
![macOS](https://img.shields.io/badge/platform-macOS-lightgrey)

## What it shows

**In the menu bar:** `◉ 42% used` — percentage of your token rate limit consumed

**Click to expand:**

```
Claude Token Tracker
─────────────────────
— Rate Limits —
Token limit: 300.0K
Remaining: 174.0K
Used: 126.0K (42%)
Resets in: 38s
─────────────────────
Request limit: 1,000
Remaining: 987
Resets in: 38s
─────────────────────
— Tracked Usage —
Today: 1.2M (47 calls)
7 days: 8.4M (312 calls)
30 days: 31.6M (1,204 calls)
─────────────────────
Status: Updated at 14:32 UTC
Refresh Now
Settings...
Quit
```

- **Rate limits** — your current token/request limits, remaining capacity, and live reset countdown
- **Tracked usage** — cumulative tokens logged locally (today, 7-day, 30-day)

## How it works

Every 5 minutes, the app makes one tiny API call (`"hi"` → 1 max token, using Haiku) and reads the rate-limit headers from the response. This costs fractions of a cent per day. It also logs each check to a local SQLite database so you can track usage over time.

## Prerequisites

- macOS 10.15+
- Python 3.9+
- An Anthropic API key (`sk-ant-api...`) from [console.anthropic.com](https://console.anthropic.com/)

## Quick start

```bash
cd macos-token-tracker

# 1. Setup (creates venv + installs deps)
chmod +x setup.sh run.sh
./setup.sh

# 2. Set your API key (or configure via Settings menu)
export ANTHROPIC_API_KEY="sk-ant-api..."

# 3. Launch
./run.sh
```

## Configuration

Click **Settings...** in the dropdown to enter your API key. Config is stored at `~/.claude-token-tracker/config.json`.

You can also set the key via environment variable:

```bash
export ANTHROPIC_API_KEY="sk-ant-api..."
```

## Menu bar states

| Icon | Meaning |
|------|---------|
| `◉ 42% used` | Normal — showing rate limit usage |
| `⏳` | Refreshing data |
| `⚠️ Key` | No API key configured |
| `⚠️ Net` | Network connection error |
| `⚠️ Err` | API error |

## Data storage

- Config: `~/.claude-token-tracker/config.json`
- Usage log: `~/.claude-token-tracker/usage.db` (SQLite)

## Cost

The probe call uses Claude Haiku with 1 max output token. At 12 checks/hour, this costs roughly **$0.01/day**.
