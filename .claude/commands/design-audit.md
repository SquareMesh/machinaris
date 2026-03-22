---
description: Audit code against design docs - find drift, gaps, and violations
allowed-tools: Read, Glob, Grep, Edit, Bash
argument-hint: [section-or-all]
---

# Design Audit

Audit design compliance for: $ARGUMENTS

If no argument provided, audit all sections in the DESIGN_INDEX.

## Steps

### 1. Load Context
Read these files:
- `.agent/DESIGN_INDEX.md` — current tracked status
- Design documents from `docs/design/`

### 2. Determine Scope
- If argument is "all": audit every section with status IN_PROGRESS, IMPLEMENTED, or VERIFIED
- If argument is a specific section: audit only that section
- Skip sections with status NOT_STARTED or DEFERRED (nothing to audit)

### 3. For Each Section in Scope

a) **Read the design doc section** — extract the concrete claims:
   - What types/interfaces should exist?
   - What module/component structure is specified?
   - What invariants or rules are stated?

b) **Check the code** — using Glob and Grep, verify:
   - Do the specified types exist at the specified locations?
   - Does the code structure match the design?
   - Are the hard rules from CLAUDE.md Section 4.2 being followed?

c) **Classify the result:**
   - `VERIFIED` — code matches design
   - `DRIFT` — code exists but diverges (describe how)
   - `PARTIAL` — some elements present, others missing
   - `VIOLATION` — a hard rule is broken (flag immediately)

### 4. Check Hard Rules (always)
Regardless of scope, verify the hard rules defined in CLAUDE.md Section 4.2 across all existing code.

### 5. Update DESIGN_INDEX
Update `.agent/DESIGN_INDEX.md` with the audit results:
- Set status for each audited section
- Update Last Verified date
- Add notes for any DRIFT or VIOLATION entries

### 6. Report

Output the audit results:

```
DESIGN AUDIT REPORT
Scope: [what was audited]
Date: [today]

VERIFIED:   [count] sections match design
DRIFT:      [count] sections diverge
  - [section]: [brief description of drift]
PARTIAL:    [count] sections incomplete
VIOLATIONS: [count] hard rule violations
  - [rule]: [where and what]

Actions required:
- [list any issues that should be logged]
```

If any VIOLATIONS found, immediately log them as CRITICAL issues using the issue format.
