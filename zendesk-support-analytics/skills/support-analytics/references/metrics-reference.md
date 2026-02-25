# Support Metrics Reference

Complete benchmark tables, industry comparisons, and glossary for the support analytics report. Include relevant sections verbatim in the report appendix.

---

## Industry Benchmark Comparison Table

| Metric | World-Class | Industry Average | Needs Attention | Critical |
|--------|-------------|-----------------|-----------------|---------|
| FCR Rate | ≥ 80% | 70–79% | 55–69% | < 55% |
| Time to First Response | < 30 min | 1–4 hours | 4–24 hours | > 24 hours |
| Mean Time to Resolution | < 8 hours | 8–24 hours | 1–3 days | > 3 days |
| Customer Satisfaction (CSAT) | ≥ 90% | 80–89% | 70–79% | < 70% |
| Ticket Reopen Rate | < 3% | 3–7% | 7–15% | > 15% |
| Stale Ticket Ratio | < 5% | 5–10% | 10–20% | > 20% |
| Agent Utilization | 70–85% | 60–75% | > 90% (burnout) | < 50% (underutilized) |

*Sources: HDI Support Center Practices & Salary Report; Zendesk Customer Experience Trends Report; Gartner IT Service Management benchmarks*

---

## Metric Definitions Glossary

Use this section verbatim in the report appendix.

**First Contact Resolution (FCR)**
The percentage of support tickets fully resolved in a single interaction, without the customer needing to contact support again for the same issue. FCR is the single most important efficiency metric in support operations — a 1% improvement in FCR typically reduces operating costs by ~1% and increases CSAT by ~1–3 points.

**Time to First Response (TTFR)**
The elapsed time between a ticket being submitted and the first public reply from a support agent. Distinct from "first reply time" in some platforms, which may count automated responses. TTFR measures human responsiveness.

**Time to Resolution (TTR) / Mean Time to Resolution (MTTR)**
The total elapsed time from ticket creation to final resolution (status: Solved or Closed). Mean TTR is sensitive to outliers; median TTR is a more reliable measure of typical performance. Both should be reported.

**Backlog**
The count of open or pending tickets at any given point. A healthy backlog grows no faster than the team can resolve tickets. Stale tickets (open > 7 days) are a leading indicator of under-resourcing or process inefficiency.

**Stale Ticket**
An open or pending ticket that has not been resolved within 7 days of creation. Stale tickets are a primary driver of low CSAT and repeat contacts. Tickets open > 14 days are classified as critical-stale.

**Ticket Reopen Rate**
The percentage of resolved tickets that are reopened because the customer's issue was not fully resolved. A high reopen rate inflates ticket volume metrics and indicates FCR overcounting.

**Infrastructure Category**
A classification applied to each ticket based on the technology area affected:
- **Network / Connectivity**: Issues with network access, VPN, DNS, firewall, Wi-Fi
- **Hardware / Endpoints**: Physical device issues — laptops, desktops, printers, peripherals
- **Software / Applications**: Application crashes, installations, licensing, performance
- **Identity & Access**: Authentication, passwords, MFA, SSO, account permissions

**Systemic Issue**
A recurring ticket cluster where 3+ tickets share the same root cause. Systemic issues warrant infrastructure remediation, not just documentation.

**Symptomatic Issue**
A recurring cluster where tickets share a symptom (e.g., "can't log in") but stem from different root causes. Symptomatic issues warrant better self-service triage and diagnostic tooling.

---

## RAG Status Definitions

Use in the Core Metrics Dashboard table:

| Status | Color | Meaning |
|--------|-------|---------|
| 🟢 Green | On track | Metric meets or exceeds benchmark |
| 🟡 Amber | Monitor | Metric is approaching the threshold — watch closely |
| 🔴 Red | Action required | Metric is below benchmark — immediate attention needed |

---

## Common Root Cause Patterns by Category

Use these to enrich the narrative sections of the report when ticket data suggests one of these patterns.

### Network / Connectivity
- **VPN instability on specific OS versions**: Often appears as a spike following OS updates. Check for driver conflicts.
- **DNS resolution failures**: Usually affects all users in a specific office or subnet. Check DHCP lease and DNS server config.
- **Wi-Fi dead zones**: Geographically clustered tickets from the same building floor or room. Check AP coverage.
- **Bandwidth saturation**: Appears as "slow internet" tickets clustering on specific times of day.

### Hardware / Endpoints
- **Aging device fleet**: Cluster of tickets from devices > 4 years old. Monitor by device age if asset tags are in ticket data.
- **Post-deployment issues**: Ticket spike after a new hardware rollout. Check deployment imaging and driver packages.
- **Printer driver conflicts**: Nearly always triggered by a Windows Update or new print server migration.
- **Docking station compatibility**: Common after laptop model transitions. Check USB-C / Thunderbolt firmware.

### Software / Applications
- **Crash after update**: Ticket spike within 24–72 hours of an application update. Roll back or patch.
- **Licensing expiry**: Cluster of "can't open [app]" tickets near license renewal dates.
- **Slow performance**: Often correlated with endpoint age, insufficient RAM, or antivirus scan scheduling.
- **Installation failures**: Frequently caused by permission restrictions (standard user accounts) or GPO conflicts.

### Identity & Access
- **MFA fatigue / enrollment issues**: High volume after MFA rollout or policy change. Provide enrollment self-service.
- **Password policy complaints**: Spike in resets after password policy tightening. Consider SSPR (Self-Service Password Reset) tooling.
- **Privilege creep and access reviews**: Slow-burn tickets about "I can't access X" — often stale permissions from role changes.
- **SSO outages**: Creates a sudden spike across all categories (users locked out of everything). Treat as P1 incident.

---

## Improvement Recommendation Templates

Use these as starting points when crafting specific recommendations.

### For High-Volume Systemic Issues
> **Investigate and remediate [issue name]** — [N] tickets in 30 days, avg TTR [X] days. Root cause appears to be [description]. Recommended action: [specific technical fix or escalation path]. Expected impact: estimated [N] ticket reduction per month if resolved.

### For Documentation Gaps
> **Create self-service guide for [topic]** — [N] tickets asking the same question. An agent-authored how-to in the Help Center could deflect an estimated [N × 0.4] tickets/month (based on industry self-service deflection rates of ~40%).

### For Process Improvements
> **Implement [process change]** — current [metric] is [X], benchmark is [Y]. Closing this gap by [specific action] is estimated to [specific outcome, e.g., reduce TTR by 20%].

### For Tooling Recommendations
> **Evaluate [tool category] solution** — [evidence from tickets]. Current workaround requires [N] agent hours/month. A dedicated solution would automate this and free agent capacity for higher-complexity tickets.
