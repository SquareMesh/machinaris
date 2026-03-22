---
description: Update a design doc and sync the design index atomically
allowed-tools: Read, Edit, Write, Glob, Grep
argument-hint: [design-doc] [section]
---

# Design Update

Update design document: $ARGUMENTS

## Purpose
When a design decision changes (via CHANGE_HISTORY), this command ensures the design doc AND the design index are updated together. Never update one without the other.

## Steps

### 1. Confirm the Change
Before modifying any design doc, verify:
- Is there a corresponding CHANGE_HISTORY entry for this change? If not, write one first.
- Is this change resolving a gap from DESIGN_REVIEW.md? If so, note which gap.
- Does this change affect other design documents? If so, list them.

### 2. Read Current State
- Read the specified design document section
- Read `.agent/DESIGN_INDEX.md` for the section's current status
- Read `.agent/CHANGE_HISTORY.md` for the relevant decision

### 3. Make the Design Doc Change
Edit the design document with the update. Preserve the document's existing format and style.

If the change resolves a gap from DESIGN_REVIEW.md:
- Update DESIGN_REVIEW.md to mark the gap as resolved with date and reference

### 4. Update the Design Index
In `.agent/DESIGN_INDEX.md`:
- Update the section's status if applicable
- Update any blocking issue references
- Set Last Verified to today's date
- Add a note if the change creates new dependencies

### 5. Cross-Reference Check
- Are any other DESIGN_INDEX sections affected by this change?
- Does this change resolve or create any OPEN_ISSUES?
- Does this change affect any existing TODO items?

### 6. Scenario Check
Consider whether this design change suggests any scenarios worth capturing:
- Does this change create an interesting decision or tension?
- Does this change cause components to interact in a new way?

If yes, capture the scenario(s) to `docs/scenarios/`. Skip if none suggested.

### 7. Confirm
Output:
```
DESIGN UPDATE
Document: [which doc]
Section: [which section]
Change: [brief description]
CHANGE_HISTORY ref: [date + title]
DESIGN_REVIEW gaps resolved: [list or "none"]
Index updated: [yes/no]
Cross-references checked: [any affected items]
Scenarios captured: [count or "none"]
```
