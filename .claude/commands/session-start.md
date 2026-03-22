---
description: Run session start protocol - check status, flag drift
allowed-tools: Grep, Glob, Read
---

# Session Start Protocol

Verify project state and report status per CLAUDE.md Section 2.

**CLAUDE.md and MEMORY.md are already loaded into context — do NOT re-read them.**

## Pre-Check: Template Configuration

First, check if CLAUDE.md contains the `TEMPLATE_UNCONFIGURED` marker (it is already in context — just check the text). If it does, this project has not been set up yet. **Stop here** and tell the user:

```
This project hasn't been configured yet. Run /setup to walk through the project setup wizard.
```

Do NOT proceed with the normal session-start protocol until `/setup` has been completed.

---

## Data Gathering

Run these searches **in parallel** (use Grep, not Read — we need counts, not full contents):

1. **DESIGN_INDEX drift/blocked** — Grep `.agent/DESIGN_INDEX.md` for `DRIFT` and `BLOCKED` (output_mode: content). Also count total rows with `|` delimited status fields.
2. **Open issues** — Grep `.agent/OPEN_ISSUES.md` for `**Priority:**` lines (output_mode: content, count).
3. **Open TODOs** — Grep `.agent/TODO.md` for `**Status:** OPEN` or `**Added:**` lines (output_mode: count).
4. **Pending follow-ups** — Grep `.agent/CHANGE_HISTORY.md` for `- \[ \]` (output_mode: content).
5. **Design review gaps** — Grep `docs/design/DESIGN_REVIEW.md` for lines containing `OPEN` (output_mode: content). Skip if file doesn't exist.
6. **File existence** — Glob for `.agent/CHANGE_HISTORY.md`, `.agent/OPEN_ISSUES.md`, `.agent/TODO.md`, `.agent/DESIGN_INDEX.md` to confirm they exist.

Only use Read if a file is missing (to report it) or if DRIFT/BLOCKED entries need more context.

## Output

```
SESSION START
Read: CLAUDE.md ✓ (preloaded) | DESIGN_REVIEW [ok/missing] | CHANGE_HISTORY [ok/missing] | OPEN_ISSUES [ok/missing] | TODO [ok/missing] | DESIGN_INDEX [ok/missing]
Design index: [N] tracked sections | [N] DRIFT | [N] BLOCKED
Open issues: [count by priority]
Open TODOs: [count]
Pending follow-ups: [count from CHANGE_HISTORY]
Open critical gaps: [list any from DESIGN_REVIEW still unresolved]
Ready for task.
```

## Conditional Steps

- If any files are **missing**: report which ones and offer to create from templates (CLAUDE.md Section 12).
- If any **DRIFT** entries exist: Read those specific DESIGN_INDEX rows and list with brief context.
- If any **CRITICAL** priority issues exist: Read those specific issue entries from OPEN_ISSUES.md.
