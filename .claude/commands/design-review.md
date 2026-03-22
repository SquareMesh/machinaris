---
description: Review all design docs for quality, gaps, blockers, inconsistencies — output to sequenced review file
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
argument-hint: [focus-area] — optional, default: all
---

# Design Review

Perform a comprehensive review of the project's design documents.

**Focus:** $ARGUMENTS (default: all design docs)

## Purpose

This is a holistic design quality review — not a code-vs-design audit (that's `/design-audit`). This review evaluates the design documents themselves: are they complete, consistent, well-reasoned, and ready to implement? It produces a durable, sequenced review file in `docs/reviews/`.

Each review is a snapshot in time. Running this again produces a new file with a new sequence number.

## Steps

### 1. Determine the next sequence number

Read the `docs/reviews/` directory. Find the highest existing 4-digit prefix. Next = highest + 1, zero-padded to 4 digits. If no review files exist, start at `0001`.

### 2. Load all design documents

Read all design documents via `docs/design/CLAUDE.md` as entry point. Read relevant section files based on the focus area (or all if no focus specified).

### 3. Load supporting context

Also read:
- `.agent/DESIGN_INDEX.md` — implementation status
- `.agent/OPEN_ISSUES.md` — known problems
- `.agent/TODO.md` — pending items
- `.agent/CHANGE_HISTORY.md` (last 10 entries) — recent decisions

### 4. Perform the review

Evaluate every design document (or the focused subset) across these dimensions:

#### A. Strengths — What is well-designed and why
#### B. Gaps — What is missing (undefined concepts, unspecified interactions, edge cases)
#### C. Inconsistencies — What conflicts (contradictions, naming mismatches, rule conflicts)
#### D. Blockers — What prevents implementation (circular dependencies, ambiguities, missing algorithms)
#### E. Improvement Opportunities — What could be better (simplification, over/under-specification)
#### F. Implementation Readiness — Rate each doc: READY | MOSTLY_READY | NEEDS_WORK | BLOCKED

### 5. Generate cross-reference matrix

Check every inter-document reference for consistency.

### 6. Compile the review file

Create `docs/reviews/[NNNN]-design-review.md` with sections for: Executive Summary, Strengths, Gaps (with severity), Inconsistencies, Blockers, Improvement Opportunities, Implementation Readiness table, Cross-Reference Issues, Priority Actions, Comparison with Previous Review.

### 7. Update tracking

- Flag any CRITICAL gaps/blockers not already in OPEN_ISSUES.md
- Flag any inconsistencies that contradict CHANGE_HISTORY decisions

### 8. Confirm

Output:
```
DESIGN REVIEW COMPLETE
File: docs/reviews/[NNNN]-design-review.md
Scope: [all | focused area]
Documents reviewed: [count]

Summary:
  Strengths:       [count]
  Gaps:            [count] ([count] CRITICAL)
  Inconsistencies: [count]
  Blockers:        [count] ([count] CRITICAL)
  Improvements:    [count]

Implementation readiness:
  READY:        [count] docs
  MOSTLY_READY: [count] docs
  NEEDS_WORK:   [count] docs
  BLOCKED:      [count] docs

Top 3 priority actions:
1. [action]
2. [action]
3. [action]

New issues to log: [count, or "none"]
```
