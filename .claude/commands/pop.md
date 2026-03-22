---
description: Recall an item from the stack (read-only, does not remove)
allowed-tools: Read, Glob
argument-hint: [number] — optional, default 1 (most recent)
---

# Pop from Stack

Read a snippet from `.agent/stack/` without removing it.

**Arguments:** $ARGUMENTS

## Argument Parsing

- **No arguments (or "1"):** Read the most recently pushed item (highest sequence ID).
- **Number N:** Read the Nth most recent item. `pop 2` = second most recent, `pop 3` = third most recent, etc.

## Steps

1. **List all files** in `.agent/stack/` sorted by filename (which sorts by sequence ID).

2. **If the stack is empty**, report: "Stack is empty. Nothing to pop."

3. **Select the target item.** Count backwards from the last file. If N exceeds the stack depth, report: "Stack only has [depth] items. Cannot pop [N]."

4. **Read the file** and present its contents.

5. **Output format:**
```
POPPED [NNNN]-[title].md (item [N] of [total])
Pushed: [date from file]
Context: [context line from file]

---
[Full content of the snippet]
---

Tip: /stack to see all items. /pop [N] to reach further back.
```
