# SDD ledger — plan: docs/superpowers/plans/2026-11-04-model-solar-science-guide.md

Pre-flight: Task 1 produces `solarGuideData.js` exports consumed by Task 2's `SolarScienceGuide`; the guide can import the module directly without adapters.

Ruling: Work directly in the user's Solaris AI project directory — its nearest Git root is the uninitialized Windows profile (`C:\Users\Nikhila Dhevi R`) containing many unrelated personal files, so making a Git worktree there would widen scope and risk collateral changes; the user explicitly designated this project directory as the deliverable.

Ruling: Replace the planned source-text test with tests of exported threshold, freshness, and filtering behavior — the frontend has no DOM test runtime, and source greps would test text rather than the user's observable behavior; navigation and layout will be checked in the running browser.

Task 1: complete — `node --test tests/solarGuideData.test.mjs` → 5 passed after the expected missing-module failure. The later A/B/C/M/X boundary test also showed the expected missing-export failure before the helper was added; final frontend suite passes 6 tests.

Task 2: complete — six frontend data/behavior tests passed; browser confirmed live measurements, all NOAA level panels, search/filter/reset, and navigation.

Task 3: complete — `npm run build` passed; desktop and 390px mobile previews showed no horizontal overflow. Reduced-motion styles are present. Existing warning: the main JS bundle is above 500 kB.

Final review: independent read-only review found no Critical or Important issues.

Final: minor (deferred): Both sub-navigation and scale selector use ARIA tab roles without arrow-key movement or linked tab panels; current controls remain operable with Tab and Enter, but the announced interaction pattern is imperfect.

Final: minor (deferred): `hasForecastAlert` is not used by the page and accepts numeric values above 1; if a future caller passes an invalid probability, it could return a false alert.

Final: Ruling: Keep the five-minute tolerance for slightly future observation timestamps — it matches the backend timestamp freshness policy and accounts for small clock skew — a larger skew than that remains unavailable.

Final: Ruling: Keep live freshness status on the app's two-minute refresh cadence — observations are refreshed every 120 seconds — stale status may therefore be displayed for up to one refresh interval.

Final: Ruling: Retain the S3 wording that spacecraft effects are "likely" — it matches NOAA's S3 scale language and the guide labels scale impacts as possible, generalized effects — actual mission outcome can differ by orbit and spacecraft design.
