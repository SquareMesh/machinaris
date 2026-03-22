---
description: Write a structured knowledge entry to docs/knowledge/
allowed-tools: Read, Write, Edit, Glob
argument-hint: [topic]
---

# Capture Knowledge Entry

Write a structured knowledge entry about: $ARGUMENTS

## Steps

1. Determine the correct subfolder based on the topic:
   - `docs/knowledge/research/` — Domain-specific research and findings
   - `docs/knowledge/patterns/` — Code patterns, architecture decisions, idioms
   - `docs/knowledge/algorithms/` — Algorithm research and comparisons
   - `docs/knowledge/tools/` — Tooling, setup, configuration notes

2. Check if a knowledge entry on this topic already exists. If so, update it rather than creating a duplicate.

3. Create the file using the format from CLAUDE.md Section 8:

```markdown
# [Topic Title]

**Category:** research | patterns | algorithms | tools
**Relevance:** [which system or design doc this supports]
**Date researched:** [today's date]

## Summary
[2-3 sentence overview of what this is and why it matters]

## Key Findings
[Bullet points of the most important facts]

## Code Example / Reference
[Minimal illustrative snippet or external link]

## Decision / Recommendation
[Should we use this? Under what conditions? Any caveats?]

## Sources
[Links or package names]
```

4. Name the file descriptively using kebab-case: e.g., `auth-jwt-vs-session.md`, `caching-redis-setup.md`

5. Confirm the entry was written and its path.
