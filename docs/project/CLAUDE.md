# Project Progress Tracking

This folder contains project-level tracking files.

## progress.html

A self-contained HTML dashboard that visualizes session history and project metrics. Open it in any browser — no server required.

### What it tracks
- **Dashboard** — summary cards (sessions, decisions, issues, TODOs, scenarios), decisions-per-session bar chart, recent sessions list
- **Timeline** — all sessions grouped by date, with session counts and decision totals per day
- **Areas** — which design docs and systems are touched most frequently (bar breakdown)
- **Metrics** — averages, issue resolution rate, cumulative trend charts (decisions, issues opened vs resolved, TODOs)
- **Session detail** — click any session row to see full detail: date, tags, summary, docs/systems touched, all metrics, commits

### How it gets updated
The `/session-end` command automatically appends a JSON session record to the `SESSIONS` array inside the file. Each record contains:

```json
{
  "session": 1,
  "date": "2026-03-10",
  "summary": "Brief description of what was done",
  "areas": {
    "docs": ["OVERVIEW", "API_DESIGN"],
    "systems": ["auth", "users"]
  },
  "metrics": {
    "decisions": 2,
    "issues_opened": 1,
    "issues_resolved": 0,
    "todos_added": 3,
    "todos_resolved": 1,
    "scenarios_added": 0
  },
  "stack_depth": 5,
  "commits": ["a1b2c3d"],
  "tags": ["design", "implementation"]
}
```

### Rules
- **Never edit session data manually** — let `/session-end` manage it
- **Session numbers are global and always increment** — never reuse or reset
- **Multiple sessions per day are fine** — each `/session-end` call creates a separate record
- The data lives between the `SESSION_DATA_START` and `SESSION_DATA_END` markers in the `<script>` block
- Everything outside those markers is the rendering logic — avoid modifying unless improving the dashboard itself

### Customization
To change the project name shown in the header, edit the `<h1>` tag in the HTML:
```html
<h1><span>Your Project</span> — Project Progress</h1>
```

To change the phase badge, edit the `.phase-badge` span:
```html
<span class="phase-badge">Phase 1 — Foundation</span>
```
