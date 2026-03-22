---
description: Capture a scenario that validates design or reveals unexpected behavior
allowed-tools: Read, Write, Edit, Glob
argument-hint: [area] [title]
---

# Capture Scenario

Capture a scenario for: $ARGUMENTS

## Purpose

Scenarios are narrative descriptions of concrete situations that validate design decisions and reveal emergent or unexpected behavior across system boundaries. They describe what should happen when components interact.

Scenarios can be discovered during design work, implementation, or testing.

Scenarios are layered:
- **Foundation** — validates existing design. The current design must support this scenario.
- **Enhancement** — extends beyond current scope. Captures "wouldn't it be great if..." grounded in concrete behavior. Notes what design work is needed.

## Steps

### 1. Determine the target file

Place scenarios in `docs/scenarios/[area]-scenarios.md` where [area] describes the system or component involved.

### 2. Determine the next scenario number

Read the target file (if it exists). Find the highest existing SC-[AREA]-NNN number. Next = highest + 1, zero-padded to 3 digits. If the file doesn't exist, start at 001.

### 3. Create or update the file

If the file doesn't exist, create it with a header:

```markdown
# [Area Name] — Scenarios

> Scenarios validating [area description].

---
```

### 4. Classify the scenario

**Layer:**
- **Foundation** — all systems involved are designed, and the scenario validates expected behavior
- **Enhancement** — involves systems not yet designed or extends beyond current scope

**Scope:**
- **IN_SCOPE** — all systems and interactions referenced exist in design docs
- **OUT_OF_SCOPE** — at least one system or interaction is not yet covered

### 5. Write the scenario

Append the scenario:

```markdown
### SC-[AREA]-[NNN]: [Descriptive Title]

**Layer:** Foundation | Enhancement
**Scope:** IN_SCOPE — [design doc(s)] | OUT_OF_SCOPE — needs [description]
**Systems:** [list all systems involved, primary first]
**Setup:** [concrete initial conditions]
**What happens:**
1. [step-by-step expected sequence of events]
2. [each step follows logically from system interactions]
3. [include decision points where choices matter]
**Expected outcome:** [what the result should be]
**Why this matters:** [rationale — what value does this scenario capture?]
**Validates:** [specific design rules, doc sections, or principles]
**Would fail if:** [concrete conditions indicating the design is broken]
```

### 6. Confirm

Output:
```
SCENARIO CAPTURED
ID: SC-[AREA]-[NNN]
Title: [title]
Layer: Foundation | Enhancement
File: docs/scenarios/[file].md
Systems: [list]
Discovered during: [design | implementation | testing]
```
