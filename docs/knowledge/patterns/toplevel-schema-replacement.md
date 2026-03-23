# TopLevelSchema — Inline Replacement for marshmallow-toplevel

**Category:** patterns
**Relevance:** API serialization layer (api/views/*/schemas.py)
**Date researched:** 2026-03-23

## Summary
The `marshmallow-toplevel` package (v0.1.3, last updated 2020) provides `TopLevelSchema` which allows marshmallow schemas to deserialize/serialize top-level JSON arrays instead of objects. It was replaced with a ~15-line inline class to remove the unmaintained dependency and unblock marshmallow 4.x upgrades.

## Key Findings
- The package defines a single class that overrides `_deserialize` and `_serialize` to delegate to a `_toplevel` Nested field
- All 21 usage sites in this codebase follow the exact same pattern: `_toplevel = ma.fields.Nested(SomeSchema, required=True, many=True)`
- The replacement class lives in `api/extensions/api/__init__.py` alongside other schema base classes
- marshmallow's `<4.0` pin was removed after this change

## Code Example / Reference
```python
class TopLevelSchema(ma.Schema):
    def _deserialize(self, data, *, many=None, partial=None, unknown=None):
        return self.fields['_toplevel']._deserialize(data, '_toplevel', data)

    def _serialize(self, obj, *, many=None):
        return self.fields['_toplevel']._serialize(obj, '_toplevel', obj)
```

## Decision / Recommendation
Inline replacement is correct. If marshmallow 4.x changes the internal `_deserialize`/`_serialize` API, this class may need updating — but it's 15 lines vs. depending on an abandoned package.

## Sources
- `marshmallow-toplevel` PyPI: https://pypi.org/project/marshmallow-toplevel/
- Previous knowledge entry: docs/knowledge/tools/marshmallow-toplevel-risk.md
