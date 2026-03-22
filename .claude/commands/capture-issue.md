---
description: Log a new issue to OPEN_ISSUES.md with auto-incrementing number
allowed-tools: Read, Edit
argument-hint: [short-title]
---

# Capture Issue

Log a new issue: $ARGUMENTS

## Steps

1. Read `.agent/OPEN_ISSUES.md` to find the current "Next issue number".

2. Ask or determine:
   - **Priority:** CRITICAL | HIGH | MEDIUM | LOW
   - **Affects:** Which component, system, or design doc
   - **Discovered during:** What task or context surfaced this
   - **Description:** Clear statement of the problem
   - **Impact:** What breaks or is blocked

3. Append the issue using the format from CLAUDE.md Section 7.1:

```markdown
---
## ISSUE-[NNN] -- [Short Title]

**Priority:** [priority]
**Status:** OPEN
**Opened:** [today's date]
**Affects:** [component / system / design doc]
**Discovered during:** [context]

### Description
[Clear statement of the problem]

### Reproduction
[Steps to reproduce, or conditions that trigger it]

### Impact
[What breaks or is blocked until this is resolved]

### Attempted Approaches
[Leave empty initially - fill in as investigation proceeds]
```

4. Increment the "Next issue number" counter in the file.

5. Check if this issue should also be reflected in `.agent/DESIGN_INDEX.md` as a blocking issue. If so, update the index.

6. Confirm: "Logged ISSUE-[NNN]: [title] at [priority] priority."
