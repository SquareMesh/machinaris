---
description: Log a lightweight TODO item for future exploration
allowed-tools: Read, Edit
argument-hint: [short-description]
---

# Capture TODO

Log a TODO item: $ARGUMENTS

## Steps

1. Read `.agent/TODO.md` to find the current "Next TODO number".

2. Append a new TODO entry:

```markdown
---
## TODO-[NNN] -- [Short Description]

**Added:** [today's date]
**Context:** [what prompted this - task, conversation, observation]
**Category:** design | implementation | research | tooling | testing
**Related:** [issue number, design doc section, or "none"]

### Notes
[Brief description of what needs to be explored or done.
This is NOT a full issue - just enough context to pick it up later.]
```

3. Increment the "Next TODO number" counter.

4. Confirm: "Logged TODO-[NNN]: [description]"

## When a TODO gets explored

If exploring a TODO reveals it's a real problem:
- Create a formal issue with `/capture-issue`
- Update the TODO entry to say: `**Status:** PROMOTED to ISSUE-[NNN]`

If exploring a TODO reveals it's not needed:
- Update the TODO entry to say: `**Status:** DISMISSED -- [brief reason]`
