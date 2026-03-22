---
description: Sync tracking files and commit - checkpoint without ending the session
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Commit Protocol

Sync all tracking files and create a git commit. This is a checkpoint — it does NOT update session memory or write the LAST SESSION block (use `/session-end` for that).

## Steps

### 1. CHANGE_HISTORY Sync
Review all decisions made since the last commit. For each functional decision (CLAUDE.md Section 6) not yet recorded, append an entry to `.agent/CHANGE_HISTORY.md`.

### 2. Issue Sync
- Were any OPEN_ISSUES resolved since last commit? Move them to RESOLVED_ISSUES.md with full resolution record.
- Were any new issues discovered? Log them to OPEN_ISSUES.md with the next sequential number.

### 3. TODO Sync
- Log any new future-work items identified since last commit to `.agent/TODO.md`.
- Update status of any TODOs that were explored (promote to issue or dismiss).

### 4. Design Index Update
For every design doc section touched since last commit:
- Update Status column in `.agent/DESIGN_INDEX.md`
- Fill in or update Code Location column
- Set Last Verified to today's date
- If code diverges from design, set status to `DRIFT`

### 5. Stage and Commit
1. Run `git status` and `git diff --cached` to review current state
2. Run `git log --oneline -3` to check recent commit message style
3. Stage all relevant changed files (be specific — avoid `git add .`)
4. Generate a commit message following the project format:
   ```
   [scope] short imperative description

   - bullet point details
   - references ISSUE-NNN if applicable
   - references CHANGE_HISTORY entry date if applicable

   Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
   ```
5. Create the commit
6. Run `git status` to verify clean state

### 6. Post-Commit Summary
Output:
```
COMMITTED [hash]
Scope: [what changed]
Tracking synced: CHANGE_HISTORY [+N] | ISSUES [N resolved, N new] | TODOs [+N] | DESIGN_INDEX [N updated]
Working tree: [clean/dirty]
```
