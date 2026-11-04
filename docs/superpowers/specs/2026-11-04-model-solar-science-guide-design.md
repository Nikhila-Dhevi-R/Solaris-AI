# Model Solar Science Guide Design

## Intent

Add a Model subpage that helps dashboard users understand NOAA solar/geomagnetic/radiation measurements, the NOAA scale thresholds and possible effects, and the separate Version 6 forecast probabilities and frozen risk boundaries.

## Goals and constraints

- Keep the guide inside the existing Model navigation area, with a clear path back to model performance.
- Define technical terms in plain language; show A/B/C/M/X X-ray flux ranges, below-scale baselines, and all five NOAA R/G/S scale levels with measurement thresholds and possible effects.
- Show live readings only from existing backend responses and label stale/missing readings clearly.
- Keep the NOAA environmental scales distinct from V6's 24-hour model thresholds: 0.205944 alert; 0.027568 Low/Moderate; 0.369991 Moderate/High.
- Style the page with warm solar color, restrained animation and translucent glass panels; honor reduced-motion preferences and preserve readability on mobile.
- Impacts are explanatory possibilities, not satellite-specific predictions, operational warnings, or commands. Cite NOAA source pages in the guide.

## Approaches

- **Chosen: nested guide in Model.** The user explicitly requested a page under Models; a subpage switcher provides room for the glossary and scale cards while keeping model metrics nearby.
- Top-level guide navigation would make it easier to discover, but would contradict the requested placement and add another global navigation entry.
- A glossary modal would be too constrained for five-level scales, live readings, and the model-threshold explanation.

## Design

Use a dedicated guide view within the existing React application. A searchable/filterable glossary explains common terms. An interactive R/G/S scale selector presents baseline and levels with exact NOAA boundaries and effects. The radio-scale view also lists the A/B/C/M/X GOES flux ranges. A live conditions strip reads the current measurements already returned by the backend. A separate V6 card explains calibrated probability, horizon, and full-precision frozen thresholds. Apply the upgraded sun/glass visual language to the dashboard shell and guide, with reduced-motion and narrow-screen fallbacks.

## Acceptance

Users can reach the guide from Model, understand all displayed measurements and thresholds, search/filter terminology, see explicit unavailable states rather than fabricated data, switch between scale groups, and return to the model overview. Threshold values and their boundary behavior are covered by automated tests; frontend build and local browser behavior are verified.

## Sources

- NOAA Space Weather Scales: https://www.swpc.noaa.gov/noaa-scales-explanation
- NOAA Planetary K-index: https://www.spaceweather.gov/products/planetary-k-index
- NOAA Space Weather Glossary: https://www.swpc.noaa.gov/content/space-weather-glossary
