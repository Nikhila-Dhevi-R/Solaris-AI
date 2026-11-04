import test from 'node:test';
import assert from 'node:assert/strict';
import {NOAA_SCALES, MODEL_THRESHOLDS, classifyFlareClass, classifyScaleValue, classifyModelRisk, hasForecastAlert, filterGlossary, liveScaleReading} from '../src/solarGuideData.js';

test('NOAA radio, geomagnetic, and radiation scales use the published five-level thresholds', () => {
  assert.deepEqual(NOAA_SCALES.radio.steps.map(step => step.threshold), [1e-5, 5e-5, 1e-4, 1e-3, 2e-3]);
  assert.deepEqual(NOAA_SCALES.geomagnetic.steps.map(step => step.threshold), [5, 6, 7, 8, 9]);
  assert.deepEqual(NOAA_SCALES.radiation.steps.map(step => step.threshold), [10, 100, 1000, 10000, 100000]);
});

test('GOES flare classes A through X transition at each exact decade boundary', () => {
  assert.deepEqual(NOAA_SCALES.radio.flareClasses.map(item => item.threshold), [0, 1e-7, 1e-6, 1e-5, 1e-4]);
  assert.equal(classifyFlareClass(0), 'A');
  assert.equal(classifyFlareClass(1e-7), 'B');
  assert.equal(classifyFlareClass(1e-6), 'C');
  assert.equal(classifyFlareClass(1e-5), 'M');
  assert.equal(classifyFlareClass(1e-4), 'X');
  assert.equal(classifyFlareClass(-1), 'Unavailable');
});

test('scale classification includes exact NOAA thresholds and keeps below-scale values distinct', () => {
  assert.equal(classifyScaleValue('radio', 1e-5), 'R1');
  assert.equal(classifyScaleValue('radio', 9.999e-6), 'Below R1');
  assert.equal(classifyScaleValue('geomagnetic', 5), 'G1');
  assert.equal(classifyScaleValue('radiation', 10), 'S1');
  assert.equal(classifyScaleValue('radiation', 999), 'S2');
  assert.equal(classifyScaleValue('unknown', 10), 'Unavailable');
  assert.equal(classifyScaleValue('radio', Number.NaN), 'Unavailable');
});

test('V6 model risk and alert boundaries remain separate and inclusive as specified', () => {
  assert.equal(MODEL_THRESHOLDS.forecastAlert, 0.20594365951619512);
  assert.equal(MODEL_THRESHOLDS.lowModerate, 0.02756797277329327);
  assert.equal(MODEL_THRESHOLDS.moderateHigh, 0.36999108243721823);
  assert.equal(classifyModelRisk(0.02756797277329326), 'Low');
  assert.equal(classifyModelRisk(0.02756797277329327), 'Moderate');
  assert.equal(classifyModelRisk(0.3699910824372181), 'Moderate');
  assert.equal(classifyModelRisk(0.36999108243721823), 'High');
  assert.equal(hasForecastAlert(0.20594365951619512), true);
  assert.equal(hasForecastAlert(0.2059436595161951), false);
});

test('glossary search and category filters find real terms and handle no matches', () => {
  assert.deepEqual(filterGlossary('protons', 'all').map(term => term.term), ['Energetic protons', 'Particle flux unit (pfu)']);
  assert.deepEqual(filterGlossary('', 'model').map(term => term.term), ['Calibrated probability', 'Forecast threshold', 'Risk band', 'Shadow mode']);
  assert.deepEqual(filterGlossary('teleportation', 'all'), []);
});

test('live scale reading rejects missing and stale data, and classifies fresh data', () => {
  const now = Date.parse('2026-11-04T12:00:00Z');
  const recent = {value: 1e-5, time: '2026-11-04T11:55:00Z'};
  assert.equal(liveScaleReading('radio', {xray: recent}, now).level, 'R1');
  assert.equal(liveScaleReading('radio', {xray: recent}, now).status, 'live');
  assert.equal(liveScaleReading('radio', {xray: {value: 1e-5, time: '2026-11-04T11:40:00Z'}}, now).status, 'unavailable');
  assert.equal(liveScaleReading('radiation', {}, now).status, 'unavailable');
  assert.equal(liveScaleReading('geomagnetic', {kp: {value: -1, time: '2026-11-04T11:59:00Z'}}, now).status, 'unavailable');
});
