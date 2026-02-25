---
description: Analyze last 30 days of Zendesk tickets and suggest new Help Center articles
allowed-tools: Bash, Write, Read
argument-hint: [optional: output filename]
---

You are running a Zendesk ticket analysis to identify gaps in the Help Center documentation.

## Step 1: Validate environment

Check that the required environment variables are set:
- `ZENDESK_SUBDOMAIN` — the subdomain portion of the Zendesk URL (e.g., `acme` for `acme.zendesk.com`)
- `ZENDESK_OAUTH_TOKEN` — a valid Zendesk OAuth access token with read access to tickets and Help Center

If either variable is missing, stop and tell the user what's missing and how to set it. Do not proceed.

## Step 2: Fetch tickets from the last 30 days

Use Bash to call the Zendesk Search API and retrieve solved or closed tickets updated within the last 30 days. Paginate through all results (up to 1,000 tickets maximum). Extract the following fields per ticket:

- `id`
- `subject`
- `description` (first 500 characters)
- `tags`
- `ticket_form_id` (if present)
- `created_at`

Run this command (replace variables as needed):

```bash
curl -s -H "Authorization: Bearer $ZENDESK_OAUTH_TOKEN" \
  "https://$ZENDESK_SUBDOMAIN.zendesk.com/api/v2/search.json?query=type:ticket+updated>$(date -d '30 days ago' +%Y-%m-%d 2>/dev/null || date -v-30d +%Y-%m-%d)&sort_by=created_at&sort_order=desc&per_page=100"
```

Handle the `next_page` field to paginate if there are more than 100 results (fetch up to 10 pages / 1,000 tickets total). If pagination fails or returns an error, proceed with what was retrieved so far.

## Step 3: Fetch existing Help Center articles

Use Bash to call the Zendesk Guide API and retrieve all published Help Center articles. Extract `id`, `title`, `section_id`, and `html_url` per article.

```bash
curl -s -H "Authorization: Bearer $ZENDESK_OAUTH_TOKEN" \
  "https://$ZENDESK_SUBDOMAIN.zendesk.com/api/v2/help_center/articles.json?per_page=100&locale=en-us"
```

Paginate until all articles are retrieved (follow `next_page`). Collect the full list of article titles for gap analysis.

## Step 4: Load the ticket-analysis skill

Before proceeding to analysis, load and apply the `ticket-analysis` skill to guide your clustering and gap analysis methodology.

## Step 5: Analyze and cluster tickets

Using the ticket-analysis skill methodology:

1. Group tickets into thematic clusters based on subject lines, tags, and descriptions. Aim for 5–20 meaningful clusters (not too granular, not too broad).
2. For each cluster, count the ticket volume and note the most common questions or pain points.
3. Sort clusters by ticket volume (highest first).

## Step 6: Identify documentation gaps

For each cluster:
1. Check whether the existing Help Center articles adequately address the topic. Perform a semantic comparison — not just exact keyword matching.
2. Mark clusters as:
   - **Gap** — no existing article covers this topic
   - **Partial** — an article exists but likely doesn't fully answer the question
   - **Covered** — a good article exists (skip these)

Focus on **Gap** and **Partial** clusters for suggestions.

## Step 7: Generate article suggestions

For each Gap or Partial cluster (up to 10 suggestions), produce:

- **Suggested article title** — clear, action-oriented (e.g., "How to reset your password on mobile")
- **Ticket volume** — number of tickets in this cluster over the last 30 days
- **Summary of the problem** — 2–3 sentences describing what customers are struggling with
- **Recommended content to cover** — 3–5 bullet points outlining what the article should include
- **Priority** — High / Medium / Low based on ticket volume and customer impact
- **If Partial**: link to the existing article that needs updating

## Step 8: Display results in chat

Present the results in this format:

```
## Zendesk Wiki Gap Analysis
**Period**: Last 30 days
**Tickets analyzed**: [N]
**Existing Help Center articles**: [N]
**Gaps identified**: [N]

---

### 🔴 High Priority

#### 1. [Suggested Article Title]
- **Ticket volume**: [N] tickets
- **Problem**: [2–3 sentence description]
- **Suggested content**:
  - [bullet 1]
  - [bullet 2]
  - [bullet 3]

---

### 🟡 Medium Priority
...

### 🟢 Low Priority
...
```

## Step 9: Save a Markdown report

After displaying in chat, save the same content as a Markdown file. If `$ARGUMENTS` was provided, use it as the filename. Otherwise default to `zendesk-wiki-suggestions-YYYY-MM-DD.md` using today's date.

Write the file to `/sessions/loving-vigilant-allen/mnt/outputs/`. Use the same structured format as Step 8 but include a header section with metadata:

```markdown
# Zendesk Help Center Gap Analysis
Generated: [date and time]
Zendesk account: [subdomain].zendesk.com
Analysis period: Last 30 days

[rest of report]
```

After saving, confirm to the user where the file was saved.

## Error handling

- If API calls return 401/403, tell the user their OAuth token may be expired or missing the required scopes (`tickets:read` and `hc:read`).
- If API calls return 429, tell the user they've hit the Zendesk rate limit and suggest retrying in a few minutes.
- If fewer than 10 tickets are returned, warn the user and proceed anyway — results may not be statistically significant.
- If the Help Center returns no articles, proceed and note in the report that no existing articles were found.
