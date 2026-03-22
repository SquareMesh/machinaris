---
description: End session - capture knowledge, update index, sync issues and todos
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Session End Protocol

Perform a thorough session wrap-up. This ensures nothing learned or decided during this session is lost.

## Steps

### 1. Knowledge Capture
Review the full conversation history for this session. For each of the following, write a knowledge entry to the appropriate `docs/knowledge/` subfolder:
- Any library or dependency researched (use or reject decision)
- Any non-trivial technical pattern discovered or applied
- Any algorithm chosen or evaluated
- Any domain-specific insight or reference found
- Any tool configuration or setup finding

Use the knowledge entry format from CLAUDE.md Section 8. Skip if nothing new was researched.

### 2. CHANGE_HISTORY Update
Review all decisions made during this session. For each functional decision (as defined in CLAUDE.md Section 6), append an entry to `.agent/CHANGE_HISTORY.md`. Decisions include:
- Choosing between implementation approaches
- Deviating from or extending a design document
- Resolving a design ambiguity
- Adding/removing/renaming public APIs, types, or interfaces
- Changing the dependency graph
- Choosing a library or dependency

### 3. Issue Sync
- Review work done: were any OPEN_ISSUES resolved? If so, move them to RESOLVED_ISSUES.md with full resolution record.
- Were any new issues discovered? Log them to OPEN_ISSUES.md with the next sequential number.
- Update the "Next issue number" counter in OPEN_ISSUES.md.

### 4. TODO Sync
- Were any new future-work items, unexplored ideas, or deferred questions identified? Log them to `.agent/TODO.md`.
- Were any existing TODOs explored and either promoted to issues or dismissed? Update their status.
- Update the "Next TODO number" counter.

### 5. Scenario Review
Review all work done this session — design decisions, implementation, testing, bug fixes. Ask:
- Did any design work reveal interesting situations worth capturing?
- Did any implementation or testing produce unexpected behavior across systems?
- Did any bug fix expose a scenario where components interact unexpectedly?

If yes, capture each scenario to `docs/scenarios/`. Skip if no new scenarios were identified.

### 6. Design Index Update
For every design doc section that was touched by work in this session:
- Update the Status column in `.agent/DESIGN_INDEX.md`
- Fill in or update the Code Location column
- Set Last Verified to today's date
- If code was written that diverges from design intent, set status to `DRIFT` and note why

### 7. Memory Update — LAST SESSION Block
This is critical for session continuity. Update the persistent memory file (`MEMORY.md` in the auto memory directory).

**The LAST SESSION block must always be the first section after the title.** Replace the existing LAST SESSION block with:

```markdown
## LAST SESSION ([today's date])
**What was done:** [1-2 sentences summarizing the session's work]
**Where we stopped:** [exactly what state things are in]
**Next steps under consideration:**
1. [Most important next step with brief reason]
2. [Second option]
3. [Third option if applicable]
**Recommended start:** [Which of the above is best to start with and why]
```

Also update other sections of MEMORY.md as needed:
- Current project phase
- Open critical issues list (add/remove as resolved)
- Any new user preferences observed
- Any new architectural decisions or conventions

### 8. Project Progress Log
Append a session record to `docs/project/progress.html` (if it exists). This tracks historical progress.

1. Read `docs/project/progress.html`
2. Find the session data array
3. Determine the next session number
4. Construct a JSON session record with: session number, date, summary, areas touched, metrics, commits, tags
5. Append the record

If the file doesn't exist, skip this step.

### 9. Session Summary
Output a brief summary:
```
SESSION END
Changes: [files created/modified count]
Knowledge entries: [count written]
CHANGE_HISTORY entries: [count added]
Issues: [resolved count] resolved, [new count] new
TODOs: [new count] new, [promoted count] promoted, [dismissed count] dismissed
Scenarios: [count captured]
Design index: [sections updated count]
Next session should: [1-2 sentence recommendation]
```
