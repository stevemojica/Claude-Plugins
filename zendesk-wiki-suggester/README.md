# Zendesk Wiki Suggester

Analyzes your Zendesk tickets from the last 30 days, compares them against your existing Help Center articles, and recommends new how-tos or wiki posts to fill the gaps — ranked by ticket volume and customer impact.

## How It Works

1. Pulls all tickets updated in the last 30 days from the Zendesk Search API
2. Pulls all published articles from your Zendesk Help Center (Guide API)
3. Clusters tickets into themes and identifies documentation gaps
4. Recommends new articles (or updates to partial ones), prioritized by volume
5. Displays results in chat and saves a Markdown report to your outputs folder

## Setup

Before using this plugin, set two environment variables:

| Variable | Description |
|----------|-------------|
| `ZENDESK_SUBDOMAIN` | Your Zendesk subdomain (e.g., `acme` for `acme.zendesk.com`) |
| `ZENDESK_OAUTH_TOKEN` | A Zendesk OAuth access token with `tickets:read` and `hc:read` scopes |

### Getting a Zendesk OAuth Token

1. Go to **Admin Center → Apps and integrations → APIs → Zendesk API**
2. Under **OAuth Clients**, create a new client or use an existing one
3. Generate a token with the scopes: `read` (covers tickets and Help Center)
4. Copy the token and set it as your environment variable

## Commands

### `/analyze-tickets`

Runs the full ticket analysis and gap report.

**Usage:**
```
/analyze-tickets
/analyze-tickets my-report.md
```

**Optional argument:** A custom filename for the Markdown output. Defaults to `zendesk-wiki-suggestions-YYYY-MM-DD.md`.

**Output:**
- A formatted gap analysis displayed in chat, grouped by priority (High / Medium / Low)
- A Markdown file saved to your outputs folder with the same content

## Skills

### `ticket-analysis`

Automatically loaded during `/analyze-tickets`. Provides the clustering methodology, documentation gap evaluation framework, and article writing guidelines used to generate high-quality suggestions.

## Rate Limits

Zendesk's API allows 700 requests per minute on most plans. This plugin uses approximately 10–20 requests per run (depending on ticket and article volume). You are unlikely to hit rate limits under normal usage.

## Troubleshooting

**401 Unauthorized** — Your OAuth token is invalid or expired. Generate a new one.

**403 Forbidden** — Your token is missing required scopes. Ensure it has `tickets:read` and `hc:read`.

**429 Too Many Requests** — You've hit the Zendesk rate limit. Wait a minute and try again.

**No suggestions returned** — Either your Help Center already covers your top ticket themes (great!) or there weren't enough tickets in the last 30 days to form meaningful clusters.
# Claude-Plugins
