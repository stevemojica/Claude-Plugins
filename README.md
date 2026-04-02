# Claude Plugins — Steve Mojica

A collection of Claude Cowork plugins for K-12 IT administrators and support teams. Built in the field running IT for a K-12 private school — these solve real problems with the tools already in front of you.

---

## Plugins

### 🔐 [k12-it-admin-plugin](./k12-it-admin-plugin)

**Microsoft 365 security auditing for K-12 IT administrators.**

Seven audit skills that connect to Microsoft Graph API and surface real threats, misconfigurations, and compliance gaps — no extra tooling, no expensive licenses, no PowerShell PhD required. Designed for schools running M365 A1/A3 Education (Entra ID P1) with limited IT staff.

| Skill | What It Does |
|-------|-------------|
| `/threat-scan` | Detects credential stuffing, impossible travel, and compromised accounts from sign-in logs |
| `/admin-role-audit` | Inventories all privileged roles and flags over-provisioned accounts |
| `/mfa-audit` | Checks MFA registration compliance against any security group |
| `/ca-audit` | Finds gaps in Conditional Access policy coverage |
| `/oauth-audit` | Reviews third-party app consents and high-risk API permissions |
| `/guest-audit` | Inventories external/guest accounts and flags stale access |
| `/inactive-accounts` | Identifies accounts inactive 30/60/90+ days and accounts that never signed in |

**Auth:** Bearer token via browser DevTools (no app registration required) or service account via Graph API.

---

### 📊 [zendesk-support-analytics](./zendesk-support-analytics)

**30-day Zendesk support intelligence report.**

Pulls FCR, TTR, ticket trends by infrastructure category, top recurring issues, and agent workload — and delivers a prioritized recommendation list plus a formatted Word doc.

**Command:** `/support-report`

---

### 📝 [zendesk-wiki-suggester](./zendesk-wiki-suggester)

**Ticket-driven Help Center article recommendations.**

Analyzes the last 30 days of Zendesk tickets, compares them against your existing Help Center articles, and recommends new how-tos to fill the gaps — ranked by ticket volume and impact.

**Command:** `/analyze-tickets`

---

## Installation

1. Download or clone this repo
2. In Claude Cowork, open **Plugins → Install from folder**
3. Point it at whichever plugin folder you want (e.g., `k12-it-admin-plugin/`)
4. Follow the setup instructions in that plugin's `README.md`

---

## Requirements

- [Claude](https://claude.ai) with Cowork mode
- Each plugin has its own connector requirements — see the individual READMEs

---

## About

Built by **Steve Mojica** — IT Director at Redlands Christian School, Redlands CA, and founder of an IT consulting practice serving K-12 Christian schools.

- GitHub: [@stevemojica](https://github.com/stevemojica)
- Contributions and issues welcome

---

## License

MIT
