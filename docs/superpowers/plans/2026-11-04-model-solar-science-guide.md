# Model Solar Science Guide Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a polished, scientifically sourced learning page nested inside Model, with live NOAA readings, searchable terminology, NOAA scale thresholds/effects, and separate V6 cutoffs.

**Architecture:** Keep the React/Vite SPA and FastAPI contracts. Put authoritative educational content and scale helpers in a pure frontend data module, render them in the existing app, and consume the already-fetched `/model`, `/conditions`, and `/satellites` responses.

**Tech Stack:** React, Vite, existing CSS, Node built-in test runner.

**Spec:** `docs/superpowers/specs/2026-11-04-model-solar-science-guide-design.md`

## Global Constraints

- Use Version 6 only; preserve its exact thresholds: 0.20594365951619512 alert, 0.02756797277329327 Low/Moderate, 0.36999108243721823 Moderate/High.
- NOAA levels are environmental scales, distinct from model probability cutoffs.
- Never imply possible effects are guaranteed or satellite-specific; no autonomous decisions.
- Use only backend data for live values; missing/stale feeds remain visibly unavailable.
- Keep the app local and responsive; reduce or disable decorative animation for `prefers-reduced-motion`.

## Review Focus

- Exact threshold equality: test R1 at 1e-5 W/m², G1 at Kp 5, and S1 at 10 pfu in the scale helpers.
- X-ray flare boundaries: test A/B/C/M/X changes at 1e-7, 1e-6, 1e-5, and 1e-4 W/m².
- Missing or stale live observations: render an unavailable label and retain educational content.
- V6 cutoffs: pin the three exact values and ensure copy labels these as probability boundaries.
- Search with no matches: show a useful empty state and allow clearing the query.
- Narrow screens/reduced motion: CSS must wrap the page and remove nonessential animation.

---

### Task 1: Educational content and threshold helpers

**Files:**
- Create: `frontend/src/solarGuideData.js`
- Create: `frontend/tests/solarGuideData.test.mjs`

**Interfaces:**
- Produces `NOAA_SCALES` including X-ray flare-class ranges, `GLOSSARY`, `MODEL_THRESHOLDS`, `classifyFlareClass(value)`, `classifyScaleValue(scaleKey, value)`, `classifyModelRisk(value)`, `hasForecastAlert(value)`, `filterGlossary(query, category)`, and `liveScaleReading(scaleKey, measurements, now)`.
- `classifyScaleValue` returns the highest reached NOAA level or the below-scale label; invalid/nonfinite input returns `Unavailable`. `liveScaleReading` rejects missing, negative, invalid-time, future, or stale measurements.

- [x] Write tests for correct R/G/S threshold arrays, exact boundary inclusivity, below-scale values, and invalid values.
- [x] Write tests for the five X-ray flare-class boundaries and exact boundary transitions.
- [x] Run `node --test tests/solarGuideData.test.mjs` from `frontend` and confirm expected failure because the module is absent.
- [x] Implement the data module using NOAA sources and the frozen V6 values in the design.
- [x] Rerun the focused test and confirm it passes.

### Task 2: Model guide page and navigation

**Files:**
- Modify: `frontend/src/main.jsx`
- Create: `frontend/src/SolarScienceGuide.jsx`
- Modify: `frontend/tests/solarGuideData.test.mjs`

**Interfaces:**
- Model navigation keeps the existing Overview and adds a Guide subview.
- Guide consumes live `conditions`, `satellites.measurements`, and `model` values already fetched by `App`.

- [x] The behavioral tests verify stale/missing live readings stay unavailable, and glossary filtering returns matches and no-match results.
- [x] The initial missing-module test run failed as expected before implementing the helper behavior.
- [x] Implement the guide, including A/B/C/M/X ranges, 15 NOAA scale levels, definitions, live-value status, and clear informational-only framing.
- [x] Manually verify Model-to-Guide navigation, search/filter, scale selection, live readings, and return navigation in the running app.
- [x] Rerun the frontend behavioral test and confirm it passes.

### Task 3: Sunlit glass visual treatment

**Files:**
- Create: `frontend/src/solarGuide.css`

**Interfaces:**
- Preserve semantic controls and text contrast while adding warm solar gradients, glass panels, soft halo/orbit motion, responsive layouts, focus-visible states, and reduced-motion support.

- [x] Add styles for the guide and refresh the existing shell/cards with restrained translucent surfaces and solar accents.
- [x] Run `npm run build` from `frontend` and confirm production assets build.
- [x] Inspect the running local app at desktop and mobile widths; check Model-to-Guide navigation, filtering, threshold switching, and reduced-motion CSS.

## Completion check

Run `npm test` and `npm run build` from `frontend`, run the backend suite, then verify the live local UI. Report any existing build warnings separately.
