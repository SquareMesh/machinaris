# marshmallow-toplevel — Unmaintained Dependency Risk

**Category:** tools
**Relevance:** docker/requirements.txt, API serialization layer
**Date researched:** 2026-03-23

## Summary
`marshmallow-toplevel` (v0.1.3, last updated November 2020) is an unmaintained package that prevents upgrading marshmallow to 4.x. It's used in the API layer for top-level list serialization.

## Key Findings
- Last PyPI release: 0.1.3 (2020-11-xx)
- No GitHub activity since 2020
- Incompatible with marshmallow 4.x (breaking API changes in marshmallow 4)
- Currently pinned: `marshmallow>=3.24.1,<4.0` to work around this
- flask-smorest 0.47.0 supports both marshmallow 3.x and 4.x

## Decision / Recommendation
Keep using marshmallow 3.x for now (it's actively maintained). When marshmallow 3.x reaches EOL or a compelling 4.x feature is needed, replace marshmallow-toplevel with inline code (it's a thin wrapper — likely < 50 lines to replace).

## Sources
- https://pypi.org/project/marshmallow-toplevel/
