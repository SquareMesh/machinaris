---
description: List all items on the push/pop stack
allowed-tools: Read, Glob
argument-hint:
---

# Stack — List All Pushed Items

Show all snippets saved to `.agent/stack/`.

## Steps

1. **List all `.md` files** in `.agent/stack/` sorted by filename (sequence ID order).

2. **If the stack is empty**, report: "Stack is empty. Use /push to save a response."

3. **For each file**, read just the header (first 6 lines) to extract:
   - Title (from `# ` line)
   - Pushed date
   - Context line

4. **Output as a numbered table**, most recent first:

```
STACK — [N] items

| # | ID   | Title                  | Pushed     | Context                          |
|---|------|------------------------|------------|----------------------------------|
| 1 | 0003 | auth-design            | 2026-03-05 | how auth flow should work...     |
| 2 | 0002 | api-rate-limiting      | 2026-03-05 | rate limiting approach...        |
| 3 | 0001 | project-setup          | 2026-03-05 | initial project decisions...     |

Use /pop [#] to recall an item.
```

The `#` column is the pop index (1 = most recent, 2 = second most recent, etc.).
