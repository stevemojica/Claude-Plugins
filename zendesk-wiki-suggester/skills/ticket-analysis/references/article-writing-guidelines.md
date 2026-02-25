# Article Writing Guidelines

Reference guide for structuring Help Center article recommendations. Use this to populate the "Recommended content to cover" section of each suggestion.

## Article Types and When to Use Each

### How-To / Step-by-Step
Use for tasks customers need to perform. Structure:
- **Title**: "How to [do X]"
- **Intro**: 1 sentence explaining what the article helps the reader do and when they'd need it
- **Prerequisites**: Any setup, permissions, or prior steps needed
- **Steps**: Numbered, one action per step, with screenshots noted if visual clarity is needed
- **Outcome**: What the customer should see/experience when done
- **Troubleshooting tips**: 2–3 common stumbling points inline

### Troubleshooting / Error Resolution
Use for known error states or confusing behavior. Structure:
- **Title**: "Why [X happens]" or "[Error message] — how to fix it"
- **Symptoms**: Exactly what the customer sees/experiences
- **Cause**: Plain-language explanation (skip jargon)
- **Fix**: Step-by-step resolution
- **If that doesn't work**: Escalation path or alternate approaches
- **Prevention**: Optional — how to avoid this in the future

### FAQ / Conceptual
Use for recurring questions that don't require steps. Structure:
- **Title**: Phrase as the customer's question
- **Direct answer**: Lead with the answer (no preamble)
- **Context / explanation**: Why this is the answer, relevant nuance
- **Related articles**: Link to how-tos if action is needed

### Reference / Policy
Use for account terms, limits, pricing questions, or policy clarifications. Structure:
- **Title**: "[Feature/Policy] — overview" or "Understanding [X]"
- **Summary**: 1–2 sentence plain-English policy statement
- **Details**: Specifics in a table or bulleted list
- **Examples**: Concrete scenarios illustrating the policy
- **Exceptions**: Edge cases or roles that are treated differently

## Content Quality Checklist

Before finalizing a suggestion's recommended content outline, verify it includes:

- [ ] A clear outcome statement (what does the customer walk away knowing/able to do?)
- [ ] At least one mention of the error message or symptom customers report verbatim (so article is findable by search)
- [ ] Coverage of the most common edge case from ticket data
- [ ] An escalation path if self-service doesn't resolve the issue
- [ ] Any platform or plan limitations that affect whether the fix applies

## Anti-Patterns to Flag

If a suggestion would result in any of these, note it in the recommendation:

- **Documentation of a bug**: Recommend filing a bug report internally instead
- **Workaround for broken UX**: Flag for product team; doc the workaround with a note that a fix is planned
- **Policy that changes frequently**: Suggest a short article that links to the source of truth (pricing page, terms doc) rather than duplicating content that goes stale
- **"Contact us" as the only answer**: If tickets cluster around something only agents can resolve (e.g., account recovery), suggest a triage article that sets expectations and collects needed info before the support handoff
