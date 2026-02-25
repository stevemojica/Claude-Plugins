---
name: ticket-analysis
description: >
  This skill should be used when analyzing support tickets to identify documentation gaps,
  when clustering Zendesk tickets by theme, when suggesting Help Center or wiki articles,
  when someone asks "what should we add to our knowledge base", or when performing
  a content gap analysis between support volume and existing documentation.
version: 0.1.0
---

# Ticket Analysis & Documentation Gap Methodology

Apply this methodology when clustering support tickets and evaluating documentation coverage gaps. This skill guides the analytical process for turning raw ticket data into actionable article suggestions.

## Core Principle

Support tickets are a signal, not noise. Each ticket represents a customer who couldn't find an answer on their own. Clusters of similar tickets reveal systematic gaps in documentation. The goal is to surface those gaps clearly so the support team can close them before more tickets pile up.

## Phase 1: Ticket Clustering

### Clustering Inputs
Use these ticket fields to form clusters:
- **Subject line** — highest signal; captures the stated problem
- **Tags** — often reflect product area or issue type already categorized by agents
- **First 500 characters of description** — captures the customer's own framing

### Clustering Rules
1. Group semantically similar tickets even if exact words differ (e.g., "can't log in", "login not working", "forgot password" may all belong to one cluster)
2. Aim for 5–20 clusters total. If you have fewer than 10 tickets, skip clustering and treat each ticket individually.
3. Do not create clusters for one-off edge cases unless volume justifies it (minimum 2+ tickets per cluster)
4. Prefer broader clusters over overly granular ones. Merge clusters that share the same root cause.
5. Name each cluster as a customer question (e.g., "How do I reset my password?" rather than "Password issues")

### Cluster Metadata to Track
For each cluster:
- Cluster name (phrased as a customer question)
- Ticket count
- Representative ticket subjects (up to 3)
- Common tags across the cluster
- Core pain point summary (1–2 sentences)

## Phase 2: Documentation Coverage Assessment

### Comparison Strategy
Do not rely on keyword matching alone. Assess whether an existing article would actually answer the customer's question by evaluating:
1. **Topic match** — does the article address the same product area or workflow?
2. **Answer completeness** — would a customer reading the article walk away with their problem solved?
3. **Freshness** — if the article seems outdated or missing recent context, flag as Partial even if the topic matches

### Coverage Categories
- **Covered** — an existing article directly and completely addresses the cluster's core question. Skip in recommendations.
- **Partial** — an article exists but only partially covers the topic, lacks specifics, or addresses a related but different question. Recommend updating it.
- **Gap** — no existing article is relevant. Recommend a new article.

### Red Flags That Indicate a Gap
- Tickets that contain phrases like "I couldn't find", "the article said to X but", "I've been looking everywhere"
- Clusters with high ticket volume but no matching article title
- Clusters where agents repeatedly post the same canned response (indicates tribal knowledge not in docs)

## Phase 3: Article Suggestion Quality

### What Makes a High-Quality Article Suggestion
A good suggestion is specific enough to be actionable. Avoid vague titles like "Billing FAQ" — prefer "How to update your payment method after a failed charge."

### Suggestion Components
Each suggestion must include:
1. **Title** — customer-facing, action-oriented, starts with "How to", "Why does", "What is", or similar
2. **Ticket volume** — raw count drives prioritization
3. **Problem summary** — written from the customer's perspective, not the internal/technical framing
4. **Recommended content outline** — 3–5 specific bullet points covering what the article should explain, including any known edge cases from the tickets
5. **Priority tier** — see below

### Priority Tiers
| Tier | Criteria |
|------|----------|
| 🔴 High | 10+ tickets in 30 days, or a cluster causing escalations or churn risk |
| 🟡 Medium | 4–9 tickets in 30 days, or a partial match needing significant updates |
| 🟢 Low | 2–3 tickets in 30 days, or a minor gap that's good to fill eventually |

## Phase 4: Avoiding Common Pitfalls

- **Don't recommend articles for known bugs** — if tickets describe a bug or outage, flag them separately rather than suggesting a "How to work around X" article. Documenting broken behavior misleads customers.
- **Don't collapse distinct problems** — if two clusters have different root causes, keep them as separate suggestions even if they appear similar.
- **Don't suggest duplicates** — check your own suggestion list for overlap before finalizing.
- **Partial coverage is often worse than no coverage** — when flagging Partials, be direct about what's missing in the existing article, not just that "it could be better."

## Reference Material

See `references/article-writing-guidelines.md` for best practices on what content to include in each article type (how-to, troubleshooting, FAQ, reference).
