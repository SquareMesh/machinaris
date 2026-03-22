---
description: Move an issue from OPEN to RESOLVED with full resolution record
allowed-tools: Read, Edit, Write
argument-hint: [issue-number]
---

# Resolve Issue

Resolve issue: $ARGUMENTS

## Steps

1. Read `.agent/OPEN_ISSUES.md` and find the specified issue (e.g., ISSUE-001).

2. If the issue is not found, report that and stop.

3. Confirm the resolution details:
   - **Root cause:** What actually caused it
   - **Fix:** What was done to resolve it
   - **Verified by:** Test, scenario, or command that confirms the fix
   - **Change history ref:** Date + title of the CHANGE_HISTORY entry if applicable

4. Add the resolution block to the issue entry:

```markdown
### Resolution
**Resolved:** [today's date]
**Root cause:** [what actually caused it]
**Fix:** [what was done]
**Verified by:** [test / scenario / command that confirms the fix]
**Change history ref:** [date + title of the CHANGE_HISTORY entry if applicable]
```

5. Remove the full issue entry from `OPEN_ISSUES.md` and append it to `RESOLVED_ISSUES.md`.

6. Update `.agent/DESIGN_INDEX.md` — if this issue was listed as a blocker for any section, update that section's status (likely from BLOCKED to NOT_STARTED or IN_PROGRESS).

7. **Knowledge check:** Did resolving this issue reveal technical rationale, research, patterns, or gotchas that would be valuable for future decisions? If yes, write a knowledge entry to `docs/knowledge/` using the format from CLAUDE.md Section 8.

8. Confirm: "Resolved ISSUE-[NNN]: [title]. Moved to RESOLVED_ISSUES.md." If a knowledge entry was written, include its path.
