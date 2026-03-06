# Claude Token Usage Tracker — macOS Menu Bar

A lightweight macOS menu bar app that shows your Anthropic API token usage and when your billing cycle resets.

![Python](https://img.shields.io/badge/python-3.9+-blue)
![macOS](https://img.shields.io/badge/platform-macOS-lightgrey)

## What it shows

- **Menu bar icon** — total tokens used this billing period (e.g. `◉ 12.4M`)
- **Billing period** — current period date range
- **Reset countdown** — live countdown to when your usage resets (e.g. `Resets in: 14d 6h 23m`)
- **Token totals** — input vs output token breakdown
- **Cost** — total spend this period in USD
- **Model breakdown** — per-model usage (Opus, Sonnet, Haiku, etc.)
- **Today's usage** — tokens consumed today

## Prerequisites

- macOS 10.15+
- Python 3.9+
- An [Anthropic Admin API key](https://console.anthropic.com/) (`sk-ant-admin...`)

> Admin API keys are available to organization admins via the Anthropic Console under **Settings → Admin API Keys**.

## Quick start

```bash
# 1. Clone and enter the directory
cd macos-token-tracker

# 2. Run setup (creates venv + installs deps)
chmod +x setup.sh run.sh
./setup.sh

# 3. Set your API key (or configure via the Settings menu)
export ANTHROPIC_ADMIN_KEY="sk-ant-admin-..."

# 4. Launch
./run.sh
```

The token icon (`◉`) will appear in your macOS menu bar. Click it to see your usage dashboard.

## Configuration

On first launch, click **Settings...** in the dropdown to enter:

1. **Admin API Key** — your `sk-ant-admin-...` key
2. **Billing cycle day** — the day of month your billing resets (default: 1st)

Settings are stored in `~/.claude-token-tracker/config.json`.

You can also set the key via environment variable:

```bash
export ANTHROPIC_ADMIN_KEY="sk-ant-admin-..."
```

## How it works

The app polls the [Anthropic Admin Usage API](https://docs.anthropic.com/en/api/usage-cost-api) every 5 minutes and displays:

- Token counts from `/v1/organizations/usage_report/messages`
- Cost data from `/v1/organizations/cost_report`

The reset countdown is calculated from your configured billing cycle day.

## Menu bar states

| Icon | Meaning |
|------|---------|
| `◉ 12.4M` | Normal — showing total tokens used |
| `⏳` | Refreshing data |
| `⚠️ Key` | No API key configured |
| `⚠️ Net` | Network connection error |
| `⚠️ Err` | API error (check Settings) |
