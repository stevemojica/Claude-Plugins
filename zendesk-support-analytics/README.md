# Zendesk Support Analytics

Generates a comprehensive 30-day support intelligence report from your Zendesk ticket data. Covers First Contact Resolution (FCR), Time to Resolution (TTR), ticket trends by infrastructure category, recurring problem patterns, agent workload, and a prioritized list of improvement recommendations. Delivers a summary in chat and a formatted Word document.

## What's in the Report

| Section | What It Covers |
|---------|----------------|
| **Executive Summary** | Narrative overview of the period's performance |
| **Core Metrics Dashboard** | FCR, TTFR, TTR (mean + median), backlog health — each with a RAG status vs. industry benchmarks |
| **Infrastructure Category Breakdown** | Ticket volume, avg TTR, and FCR by: Network/Connectivity, Hardware/Endpoints, Software/Applications, Identity & Access |
| **Top Recurring Issues** | Top 10 ticket clusters ranked by volume, classified as Systemic or Symptomatic |
| **Agent & Workload Analysis** | Ticket distribution per agent, overload flags, unassigned ticket alerts |
| **Prioritized Recommendations** | Up to 8 actionable improvement items ranked 🔴 High / 🟡 Medium / 🟢 Low |
| **Appendix: Metric Definitions** | Self-contained glossary for stakeholder distribution |

## Setup

Set these two environment variables before running:

| Variable | Description |
|----------|-------------|
| `ZENDESK_SUBDOMAIN` | Your Zendesk subdomain only — e.g., `acme` for `acme.zendesk.com` |
| `ZENDESK_OAUTH_TOKEN` | A Zendesk OAuth token with `tickets:read` scope |

### Getting a Zendesk OAuth Token

1. **Admin Center → Apps and integrations → APIs → Zendesk API**
2. Under **OAuth Clients**, create or select a client
3. Generate a token with `read` scope (covers tickets, users, and comments)
4. Set `ZENDESK_OAUTH_TOKEN` to this value in your environment

### Setting Environment Variables

**macOS / Linux:**
```bash
export ZENDESK_SUBDOMAIN=acme
export ZENDESK_OAUTH_TOKEN=your_token_here
```

Add these to `~/.zshrc` or `~/.bash_profile` to persist them.

**Windows (Command Prompt):**
```
setx ZENDESK_SUBDOMAIN acme
setx ZENDESK_OAUTH_TOKEN your_token_here
```

## Commands

### `/support-report`

Runs the full 30-day analytics workflow and generates the report.

**Usage:**
```
/support-report
/support-report Q1-support-review.docx
```

**Optional argument:** Custom filename for the Word document output. Defaults to `zendesk-support-report-YYYY-MM-DD.docx`.

**What it does, step by step:**
1. Validates environment variables
2. Fetches up to 1,000 tickets from the past 30 days
3. Samples up to 200 tickets for FCR calculation (checks comment counts)
4. Fetches agent/user data for workload analysis
5. Categorizes every ticket into an infrastructure area
6. Computes all metrics using the support-analytics skill methodology
7. Identifies recurring issue clusters and classifies them as Systemic vs. Symptomatic
8. Generates prioritized improvement recommendations
9. Displays a summary in chat
10. Produces a formatted `.docx` report in your outputs folder

**Typical runtime:** 2–4 minutes depending on ticket volume and API response times.

## Skills

### `support-analytics`

Loaded automatically during `/support-report`. Contains:
- FCR, TTFR, and TTR formulas and classification rules
- Industry benchmark tables
- Infrastructure categorization logic (with priority-matching order)
- Trend analysis framework (15-day split comparison)
- Systemic vs. Symptomatic issue classification
- Improvement prioritization matrix
- Recommendation writing standards

## API Usage

This plugin makes approximately 15–30 Zendesk API calls per run:
- 1–10 calls for ticket pagination (100 tickets/page)
- 1 call for agent list
- Up to 10 calls for FCR comment sampling (batched)

Zendesk allows 700 requests/minute on most plans. This plugin will not hit rate limits under normal usage.

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| 401 Unauthorized | Token invalid or expired | Generate a new OAuth token |
| 403 Forbidden | Token missing `tickets:read` scope | Regenerate with correct scope |
| 429 Too Many Requests | Rate limit hit | Wait 60 seconds and retry |
| `python-docx not found` | pip install failed | Report falls back to Markdown; install python-docx manually with `pip install python-docx` |
| Fewer than 20 tickets | Not enough data in period | Report runs but flags low statistical confidence |
| FCR shows "insufficient data" | Too few comment fetches succeeded | Expected on free Zendesk plans with limited API access |

## Pairing with Zendesk Wiki Suggester

This plugin pairs well with `zendesk-wiki-suggester`. A typical workflow:
1. Run `/support-report` to identify your top recurring issues and improvement areas
2. Run `/analyze-tickets` to identify which of those issues lack Help Center documentation
3. Use both outputs together to plan your support improvement sprint
