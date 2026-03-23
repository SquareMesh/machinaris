# Bootstrap Icons Font Download — v1.13.1+ Format Change

**Category:** tools
**Relevance:** Build system (scripts/pull_3rd_party_libs.sh)
**Date researched:** 2026-03-23

## Summary
Bootstrap Icons v1.13.1 changed the GitHub release zip to contain only SVG files — the font files (CSS, woff, woff2) used by the web UI are no longer in the zip. Font assets must be downloaded separately from the jsDelivr CDN.

## Key Findings
- GitHub release zip (`bootstrap-icons-X.Y.Z.zip`) = SVGs only, flat directory
- Font CSS + woff files are on jsDelivr npm CDN: `cdn.jsdelivr.net/npm/bootstrap-icons@VERSION/font/`
- The old script expected `icons/font/` subdirectory in the zip — this no longer exists
- Templates reference `3rd_party/icons/bootstrap-icons.css` which loads woff2 from `fonts/` relative path

## Code Example / Reference
```bash
# Correct approach (direct CDN download):
mkdir -p ${BASEPATH}/icons/fonts
wget -nv -O ${BASEPATH}/icons/bootstrap-icons.css \
  "https://cdn.jsdelivr.net/npm/bootstrap-icons@${BSI_VERSION}/font/bootstrap-icons.css"
wget -nv -O ${BASEPATH}/icons/fonts/bootstrap-icons.woff2 \
  "https://cdn.jsdelivr.net/npm/bootstrap-icons@${BSI_VERSION}/font/fonts/bootstrap-icons.woff2"
```

## Decision / Recommendation
Always use jsDelivr CDN for font files. If upgrading BSI_VERSION, verify the CDN paths still exist. The SVG zip from GitHub is not needed for this project.

## Sources
- jsDelivr CDN: https://cdn.jsdelivr.net/npm/bootstrap-icons@1.13.1/font/
- GitHub release: https://github.com/twbs/icons/releases/tag/v1.13.1
