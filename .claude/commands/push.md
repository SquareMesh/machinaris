---
description: Save a response to the stack for later recall
allowed-tools: Read, Write, Glob
argument-hint: [number] [title] — both optional
---

# Push to Stack

Save a response snippet to `.agent/stack/` for later recall via `/pop`.

**Arguments:** $ARGUMENTS

## Argument Parsing

Parse $ARGUMENTS to determine:
- **No arguments:** Save the most recent assistant response. Auto-generate a short title from the content.
- **Just a title (non-numeric text):** Save the most recent assistant response with the given title.
- **Just a number N:** Save the Nth most recent assistant response (1 = last, 2 = second last, etc.). Auto-generate title.
- **Number N followed by text:** Save the Nth most recent assistant response with the given title.

Examples:
- `/push` — saves last response, auto-titled
- `/push auth design` — saves last response, titled "auth-design"
- `/push 3` — saves 3rd most recent response, auto-titled
- `/push 3 auth design` — saves 3rd most recent response, titled "auth-design"

## Steps

1. **Identify the target response.** Count back through assistant responses in the conversation to find the correct one. Skip any responses that are purely tool-call mechanics — find substantive assistant text.

2. **Determine the next sequence ID.** Read `.agent/stack/` directory listing. Find the highest existing 4-digit ID prefix. Next ID = highest + 1, zero-padded to 4 digits. If no files exist, start at `0001`.

3. **Generate the title.** If the user provided a title, convert to kebab-case. If not, read the response content and generate a short (2-4 word) kebab-case summary.

4. **Create the snippet file** at `.agent/stack/[NNNN]-[kebab-title].md`:

```markdown
# [Human-readable title]

**Pushed:** [today's date]
**Source:** Response [N] in conversation (counting back from most recent)
**Context:** [The user's question/prompt that triggered this response — keep it brief]

---

[Full content of the assistant response, preserving formatting]
```

5. **Confirm:**
```
PUSHED [NNNN]-[title].md
Content: [first ~50 chars of the response]...
Stack depth: [total files in .agent/stack/]
```
