---
name: support-analytics
description: >
  This skill should be used when computing Zendesk support metrics, when calculating
  FCR (First Contact Resolution) or TTR (Time to Resolution), when generating a 30-day
  support trends report, when analyzing ticket volume by infrastructure category,
  when identifying recurring issues or systemic problems, when someone asks "how is
  our support team performing", or when producing improvement recommendations from
  ticket data.
version: 0.1.0
---

# Support Analytics Methodology

This skill governs how to compute, interpret, and present support performance metrics from Zendesk ticket data. Apply it whenever producing any report, trend analysis, or recommendation set from ticket data.

## Metric Definitions and Formulas

### First Contact Resolution (FCR)

**Definition**: The percentage of support tickets resolved completely in a single agent interaction, without the customer needing to follow up.

**Formula**:
```
FCR Rate = (Tickets resolved with ≤1 public agent reply / Total resolved tickets sampled) × 100
```

**Rules for classification**:
- A ticket is FCR = true if: status is `solved` or `closed` AND the ticket has exactly 1 public comment authored by an agent
- A ticket is FCR = false if: the customer replied after the agent, requiring a second agent response
- Tickets with only internal notes (no public replies) are excluded from the FCR denominator
- Tickets escalated between agents count as NOT resolved on first contact

**Benchmarks**:
| FCR Rate | Assessment |
|----------|-----------|
| ≥ 75% | Excellent |
| 65–74% | Good |
| 55–64% | Needs improvement |
| < 55% | Critical — investigate immediately |

---

### Time to First Response (TTFR)

**Definition**: Time elapsed between ticket creation and the first public agent reply.

**Calculation**: `first_agent_comment_timestamp - ticket.created_at` (in hours)

**When exact data is unavailable**: Estimate TTFR using `ticket.updated_at - ticket.created_at` for tickets with exactly 1 comment and status `solved`. Flag these as estimated.

**Benchmarks**:
| TTFR | Assessment |
|------|-----------|
| < 1 hour | Excellent |
| 1–4 hours | Good |
| 4–8 hours | Acceptable |
| 8–24 hours | Needs improvement |
| > 24 hours | SLA risk — flag individually |

---

### Time to Resolution (TTR)

**Definition**: Total elapsed time from ticket creation to final resolution.

**Calculation**: `ticket.updated_at - ticket.created_at` for tickets with status `solved` or `closed` (in hours, converted to days + hours for display)

**Use both mean and median**:
- Mean is sensitive to outliers (one 30-day-old ticket skews it heavily)
- Median is the more reliable central tendency for TTR
- If mean > 2× median, note that outliers are inflating the average

**Benchmarks**:
| TTR | Assessment |
|-----|-----------|
| < 4 hours | Excellent |
| 4–24 hours | Good |
| 1–3 days | Acceptable |
| 3–7 days | Needs improvement |
| > 7 days | Critical — flag tickets individually |

---

### Backlog Health

**Stale ticket threshold**: Open or pending tickets with `created_at` > 7 days ago
**Critical threshold**: Open or pending tickets with `created_at` > 14 days ago

**Healthy backlog ratio**: Stale tickets should be < 10% of total open tickets.
If stale tickets exceed 20% of open tickets, flag as a critical backlog problem.

---

## Infrastructure Categorization Rules

Use this hierarchy to assign each ticket to a category. Apply the first matching rule.

### Priority matching order:
1. **Identity & Access** — match first because "can't log in" tickets often have IT-related tags or keywords like `password_reset`, `mfa`, `sso`, `locked_out`, `permissions`, `account_access`
2. **Network / Connectivity** — match keywords: `vpn`, `wifi`, `network`, `internet`, `dns`, `firewall`, `bandwidth`, `latency`, `offline`, `connection`, `ping`, `no_internet`
3. **Software / Applications** — match keywords: `app`, `software`, `install`, `crash`, `update`, `license`, `performance`, `error_code`, `slow`, `freeze`, `application`, `program`
4. **Hardware / Endpoints** — match keywords: `laptop`, `desktop`, `computer`, `monitor`, `printer`, `mouse`, `keyboard`, `hardware`, `device`, `screen`, `battery`, `peripheral`, `docking_station`
5. **Uncategorized** — no clear match

**Tie-breaking rule**: If a ticket matches multiple categories, use the first in the priority list above. The logic is that access issues are highest-friction for users and most likely to be the real root problem.

---

## Trend Analysis Framework

When analyzing week-over-week or category trends:

1. **Split the 30-day window into two 15-day halves**: days 1–15 (earlier period) vs. days 16–30 (recent period)
2. **Compute volume change**: `(recent_half_tickets - earlier_half_tickets) / earlier_half_tickets × 100`
3. **Classify trends**:
   - > +20%: Significant increase 📈 — investigate root cause
   - +5% to +20%: Moderate increase
   - -5% to +5%: Stable
   - -5% to -20%: Moderate decrease (positive sign)
   - < -20%: Significant decrease 📉 — confirm not masking unreported issues

4. **Look for spikes**: If any single day has > 3× the daily average, flag it as an anomaly worth investigating (may indicate an outage or a deployment that caused issues)

---

## Issue Classification: Systemic vs. Symptomatic

Apply this classification to recurring issue clusters:

### Systemic Issues
- Same root cause appearing in 3+ tickets
- Often share identical or near-identical subject lines
- Same tag appears in ≥ 80% of the cluster
- Resolution time tends to be similar across tickets (agents following same workaround)
- **Treatment**: Recommend an infrastructure fix or permanent solution, not just better docs

### Symptomatic Issues
- Multiple tickets share a symptom but come from different root causes
- Subject lines are similar but descriptions differ significantly
- Mix of tags across tickets
- Resolution times vary widely
- **Treatment**: Recommend self-service documentation, triage scripts, or diagnostic tooling

---

## Improvement Prioritization Framework

Use this matrix to assign priority to recommendations:

| Criterion | High 🔴 | Medium 🟡 | Low 🟢 |
|-----------|---------|-----------|-------|
| Ticket volume | 10+ tickets on this issue | 4–9 tickets | 1–3 tickets |
| Customer impact | Business-blocking or data access risk | Workflow disruption | Minor inconvenience |
| Resolution complexity | Quick fix available | Moderate effort required | Requires long-term planning |
| SLA risk | TTR or TTFR above benchmark | Approaching benchmark | Within benchmark |
| Recurrence | Same issue in multiple weeks | Same issue twice | First occurrence |

**Default to High** if any of the following are true:
- A single issue accounts for > 15% of all tickets
- Any ticket in the cluster has been open > 14 days
- The cluster maps to Identity & Access (authentication issues block all other work)

**Recommendation writing rule**: Every recommendation must name a specific action, not just a problem. "Fix VPN" is not a recommendation. "Investigate and patch the Windows 11 sleep-mode VPN disconnect (affects 23 tickets; avg TTR 3.2 days)" is a recommendation.

---

## Reference Material

See `references/metrics-reference.md` for complete benchmark tables, industry comparisons, and a definitions glossary suitable for inclusion in stakeholder reports.
