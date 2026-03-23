# Removing |safe Filters from Jinja2 Templates

**Category:** patterns
**Relevance:** CONFIGURATION.md §6 (Security), XSS prevention
**Date researched:** 2026-03-22

## Summary
Jinja2's `|safe` filter disables auto-escaping, creating XSS vectors. When templates use `|safe` because Python code embeds HTML in variables, the fix is to move the safety decision to the Python source rather than the template.

## Key Findings
- Two patterns replace `|safe`:
  1. **Category suffixes for flash messages** — e.g., `flash(text, 'danger_pre')` instead of `flash('<pre>'+text+'</pre>', 'danger')`. Template macro checks suffix and wraps content.
  2. **`markupsafe.Markup()`** — wraps trusted HTML at the source. Jinja2 skips auto-escaping for `Markup` objects but escapes everything else. Use `Markup('...').format(var)` to auto-escape interpolated values.
- `Markup()` is safer than `|safe` because the trust decision is made where the HTML is created, not where it's rendered
- A shared Jinja2 macro (`_flash_messages.html`) can replace copy-pasted flash blocks across many templates
- `markupsafe` is already a Flask dependency — no new package needed

## Code Example
```python
# Before (unsafe)
flash('<pre>{}</pre>'.format(error_text), 'danger')
# Template: {{ message|safe }}

# After (safe — category suffix)
flash(error_text, 'danger_pre')
# Template macro checks category.endswith('_pre') and wraps in <pre>

# Before (unsafe)
return '<a href="{}">link</a>'.format(url)
# Template: {{ value|safe }}

# After (safe — Markup)
from markupsafe import Markup
return Markup('<a href="{}">link</a>').format(url)
# Template: {{ value }}  (auto-escaping skipped for Markup objects)
```

## Decision / Recommendation
Always prefer `Markup()` at the Python source over `|safe` in templates. For flash messages with formatting needs, use category suffixes with template-side rendering. This pattern eliminated all 22 `|safe` occurrences in Machinaris templates.

## Sources
- markupsafe docs: https://markupsafe.palletsprojects.com/
- Flask security docs on XSS: https://flask.palletsprojects.com/en/latest/security/
