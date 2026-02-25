---
description: Generate a 30-day Zendesk support analytics report with FCR, TTR, trends, and improvements
allowed-tools: Bash, Write, Read
argument-hint: [optional: output filename]
---

You are generating a comprehensive 30-day Zendesk support intelligence report. This report surfaces operational metrics (FCR, TTR), ticket trends by infrastructure category, recurring problem patterns, and prioritized improvement recommendations.

Load and apply the `support-analytics` skill before beginning analysis.

---

## Step 1: Validate Environment

Check that both environment variables are set:
- `ZENDESK_SUBDOMAIN` — subdomain only (e.g., `acme` for `acme.zendesk.com`)
- `ZENDESK_OAUTH_TOKEN` — OAuth access token with `tickets:read` scope

If either is missing, stop and tell the user exactly what's needed and how to set it. Do not proceed.

---

## Step 2: Establish Date Range

Calculate the 30-day window:
- **End date**: today
- **Start date**: 30 days ago

Use Bash to get formatted dates:
```bash
END_DATE=$(date +%Y-%m-%d)
START_DATE=$(date -d '30 days ago' +%Y-%m-%d 2>/dev/null || date -v-30d +%Y-%m-%d)
echo "Range: $START_DATE to $END_DATE"
```

---

## Step 3: Fetch Ticket Data

Retrieve all tickets created within the 30-day window. Paginate through results (up to 10 pages / 1,000 tickets). For each ticket, collect:

| Field | Purpose |
|-------|---------|
| `id` | Unique identifier |
| `subject` | Theme clustering |
| `description` (first 300 chars) | Problem categorization |
| `tags` | Category mapping |
| `status` | Open / pending / solved / closed |
| `created_at` | Volume trending |
| `updated_at` | Activity recency |
| `assignee_id` | Agent workload |
| `requester_id` | Repeat-contact detection |
| `ticket_form_id` | Form-based category hints |

```bash
curl -s -H "Authorization: Bearer $ZENDESK_OAUTH_TOKEN" \
  "https://$ZENDESK_SUBDOMAIN.zendesk.com/api/v2/search.json?query=type:ticket+created>$START_DATE&per_page=100&sort_by=created_at&sort_order=asc"
```

Store all ticket data in memory. Track the total count.

---

## Step 4: Fetch Ticket Comments (for FCR Calculation)

For FCR, you need comment counts per ticket. To avoid excessive API calls, sample the first 200 tickets (or all tickets if fewer than 200). For each sampled ticket, retrieve its comment count:

```bash
curl -s -H "Authorization: Bearer $ZENDESK_OAUTH_TOKEN" \
  "https://$ZENDESK_SUBDOMAIN.zendesk.com/api/v2/tickets/{TICKET_ID}/comments.json?per_page=2"
```

A ticket counts as "First Contact Resolved" if:
- It has exactly 1 public comment from an agent (the resolution)
- AND its status is `solved` or `closed`

Track: FCR count and total resolved tickets sampled.

---

## Step 5: Fetch Agent/User Data

Retrieve agent names to map `assignee_id` values for the workload section:

```bash
curl -s -H "Authorization: Bearer $ZENDESK_OAUTH_TOKEN" \
  "https://$ZENDESK_SUBDOMAIN.zendesk.com/api/v2/users.json?role=agent&per_page=100"
```

---

## Step 6: Load the support-analytics Skill

Before proceeding to analysis, confirm the `support-analytics` skill is loaded. Apply its FCR formula, TTR calculation method, trend analysis framework, and infrastructure categorization rules throughout Steps 7–10.

---

## Step 7: Compute Core Metrics

Using the fetched data and the support-analytics skill methodology, calculate:

### 7a. Volume Metrics
- Total tickets created in period
- Tickets by status (open / pending / solved / closed)
- Daily average ticket volume
- Week-over-week trend (compare weeks 1–2 vs. weeks 3–4 within the 30-day window)

### 7b. First Contact Resolution (FCR)
Apply the FCR formula from the support-analytics skill:
- FCR Rate = (Tickets resolved in 1 agent reply / Total resolved tickets sampled) × 100
- Flag if sample < 50 tickets (results less statistically reliable)
- Benchmark: Industry average FCR is ~70–75%; flag if below 60%

### 7c. Time to First Response (TTFR)
- Use `created_at` vs. the timestamp of the first agent comment (estimated from ticket `updated_at` for tickets with 1 comment, or note as estimated)
- Calculate mean and median TTFR in hours
- Flag tickets with TTFR > 24 hours as SLA-risk

### 7d. Time to Resolution (TTR)
- Use `created_at` vs. `updated_at` for solved/closed tickets only
- Calculate mean and median TTR in hours and in days
- Identify the slowest 10% of tickets by TTR

### 7e. Backlog Health
- Count of open + pending tickets at end of period
- Tickets open > 7 days (stale tickets)
- Tickets open > 14 days (critical backlog)

---

## Step 8: Categorize Tickets by Infrastructure Area

Map each ticket into one of the four infrastructure categories using subject, description, and tags. Apply the categorization rules from the support-analytics skill:

| Category | Keywords / Tag Signals |
|----------|----------------------|
| **Network / Connectivity** | vpn, wifi, network, internet, firewall, dns, bandwidth, connectivity, ping, latency, offline |
| **Hardware / Endpoints** | laptop, desktop, computer, monitor, printer, mouse, keyboard, hardware, device, screen, battery, peripheral |
| **Software / Applications** | app, software, install, crash, update, license, performance, error, application, program, slow, freeze |
| **Identity & Access** | password, login, access, mfa, sso, account, locked, permission, reset, authentication, 2fa, credentials |

For tickets that don't clearly match any category, label them **Uncategorized** and list the top 5 in the report.

For each category, compute:
- Ticket count and % of total
- Average TTR
- FCR rate (if enough data)
- Top 3 recurring subjects

---

## Step 9: Identify Recurring Issues and Improvement Areas

### 9a. Top Recurring Problems
Cluster tickets by semantic similarity (subject + tags). Identify the top 10 clusters by volume. For each:
- Cluster name (as a plain-English problem statement)
- Ticket count
- Category
- Average resolution time
- Whether it appears to be a fixable systemic issue vs. a one-off

### 9b. Systemic vs. Symptomatic Issues
Apply the support-analytics classification framework:
- **Systemic** — same root cause appears in 3+ tickets (e.g., "VPN drops on Windows 11 after sleep"). These warrant an infrastructure fix.
- **Symptomatic** — tickets share a symptom but have different causes (e.g., various "can't log in" reasons). These warrant better documentation or a self-service reset flow.

### 9c. Agent Workload Distribution
- Ticket count per agent
- Flag if any agent has >40% of total volume (overload risk)
- Flag if any tickets are unassigned for >48 hours

---

## Step 10: Generate Improvement Recommendations

Based on findings from Steps 7–9, produce a prioritized list of up to 8 recommendations. Each recommendation must include:

- **Title** — one-line action item
- **Category** — which infrastructure area it affects (or "Operations" for process issues)
- **Supporting evidence** — specific metric or ticket pattern that surfaces this issue
- **Recommended action** — what to do about it
- **Priority** — 🔴 High / 🟡 Medium / 🟢 Low (based on volume, customer impact, and SLA risk)

Apply the improvement prioritization framework from the support-analytics skill.

---

## Step 11: Display Summary in Chat

Present the report in chat using this format:

```
## 📊 30-Day Support Intelligence Report
**Period**: [START_DATE] – [END_DATE]
**Total tickets analyzed**: [N]
**Generated**: [timestamp]

---

### 📈 Key Metrics
| Metric | Value | Benchmark |
|--------|-------|-----------|
| Total Tickets | N | — |
| FCR Rate | X% | ~70–75% |
| Avg Time to First Response | Xh | <4h |
| Avg Time to Resolution | Xd Xh | <2d |
| Median TTR | Xd Xh | — |
| Stale Tickets (>7d open) | N | <10% of backlog |

---

### 🏗️ Tickets by Infrastructure Category
| Category | Tickets | % of Total | Avg TTR |
|----------|---------|------------|---------|
| Network / Connectivity | N | X% | Xh |
| Hardware / Endpoints | N | X% | Xh |
| Software / Applications | N | X% | Xh |
| Identity & Access | N | X% | Xh |
| Uncategorized | N | X% | — |

---

### 🔁 Top Recurring Issues
1. [Problem] — N tickets — [Category]
2. ...

---

### 🔴 Priority Improvements
1. [Title] — [Category] — [1-line rationale]
2. ...
```

---

## Step 12: Generate Word Document Report

Install python-docx if needed:
```bash
pip install python-docx --break-system-packages -q 2>/dev/null || true
```

Write and execute a Python script that generates a formatted `.docx` report. The document must include:

**Cover section:**
- Title: "30-Day Support Intelligence Report"
- Subtitle: "[ZENDESK_SUBDOMAIN] — [START_DATE] to [END_DATE]"
- Generated date and ticket count

**Section 1 — Executive Summary**
A 2–3 paragraph narrative summarizing the period: volume, overall FCR and TTR performance vs. benchmarks, the biggest problem category, and the top 1–2 recommended actions.

**Section 2 — Core Metrics Dashboard**
A table with all key metrics (FCR, TTFR, TTR mean/median, backlog, stale tickets) with benchmark comparisons and a RAG (Red/Amber/Green) status column.

**Section 3 — Infrastructure Category Breakdown**
A table showing each category's ticket count, %, avg TTR, FCR rate, and a "Top Issue" column. Below the table, include a 2–3 sentence narrative for each category that explains the main pain point and trend.

**Section 4 — Top Recurring Issues**
A numbered list of the top 10 recurring issues. For each: problem statement, ticket count, category, average TTR, and a one-sentence "Root cause or pattern" note.

**Section 5 — Agent & Workload Analysis**
A table showing ticket distribution by agent with workload flags. A note on unassigned tickets.

**Section 6 — Prioritized Improvement Recommendations**
All recommendations from Step 10, formatted as a table with columns: Priority, Title, Category, Evidence, Recommended Action.

**Section 7 — Appendix: Metric Definitions**
Include definitions for FCR, TTFR, TTR, and backlog health so the report is self-contained for stakeholders.

Use professional formatting: heading styles (Heading 1 for sections, Heading 2 for subsections), table grid style, 1-inch margins, 11pt Calibri body text.

If `$ARGUMENTS` was provided, use it as the filename. Otherwise default to `zendesk-support-report-YYYY-MM-DD.docx`.

Save to `/sessions/loving-vigilant-allen/mnt/outputs/`.

Confirm to the user where the file was saved.

---

## Error Handling

- **401/403**: Token invalid or missing `tickets:read` scope — tell the user and stop.
- **429**: Rate limit hit — tell the user to wait 1 minute and retry.
- **python-docx install fails**: Fall back to saving a Markdown file instead and notify the user.
- **Fewer than 20 tickets**: Proceed but note that metrics may not be statistically meaningful.
- **FCR sample too small** (< 10 comment fetches succeed): Report FCR as "insufficient data" rather than a misleading number.
- **Date flag issues on macOS vs. Linux**: Handle both `date -d` (Linux) and `date -v` (macOS) syntax gracefully.
