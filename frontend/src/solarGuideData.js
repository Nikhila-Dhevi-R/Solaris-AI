export const MODEL_THRESHOLDS = Object.freeze({
  forecastAlert: 0.20594365951619512,
  lowModerate: 0.02756797277329327,
  moderateHigh: 0.36999108243721823,
});

export const NOAA_SCALES = Object.freeze({
  radio: {
    key: 'radio', code: 'R', title: 'Radio blackouts', category: 'radio', measurementKey: 'xray',
    measurement: 'GOES 0.1–0.8 nm X-ray flux', unit: 'W/m²', maxAgeMinutes: 15,
    baseline: 'Below M1 (1 × 10⁻⁵ W/m²): below the first NOAA R-scale threshold.',
    description: 'X-rays from a flare reach Earth in about eight minutes and increase ionization on the sunlit side. The R-scale describes possible radio and navigation effects; it does not measure a satellite’s health.',
    flareClasses: [
      {letter:'A',threshold:0,range:'< 1 × 10⁻⁷ W/m²',meaning:'The quietest named X-ray class; below the NOAA R1 radio-blackout threshold.'},
      {letter:'B',threshold:1e-7,range:'1 × 10⁻⁷ to < 1 × 10⁻⁶ W/m²',meaning:'A low X-ray flux band; below the NOAA R1 radio-blackout threshold.'},
      {letter:'C',threshold:1e-6,range:'1 × 10⁻⁶ to < 1 × 10⁻⁵ W/m²',meaning:'A stronger X-ray band, still below the R1 boundary at M1.'},
      {letter:'M',threshold:1e-5,range:'1 × 10⁻⁵ to < 1 × 10⁻⁴ W/m²',meaning:'M1 is the first NOAA R-scale threshold; radio effects are possible on the sunlit side.'},
      {letter:'X',threshold:1e-4,range:'≥ 1 × 10⁻⁴ W/m²',meaning:'X1 reaches the R3 threshold; effects depend on the event, location, and duration.'},
    ],
    steps: [
      {level:'R1',descriptor:'Minor',threshold:1e-5,thresholdLabel:'M1 · 1 × 10⁻⁵ W/m²',effects:'Weak or minor HF radio degradation on the sunlit side; low-frequency navigation may be briefly degraded.'},
      {level:'R2',descriptor:'Moderate',threshold:5e-5,thresholdLabel:'M5 · 5 × 10⁻⁵ W/m²',effects:'Limited HF radio blackout on the sunlit side, lasting tens of minutes; low-frequency navigation can degrade.'},
      {level:'R3',descriptor:'Strong',threshold:1e-4,thresholdLabel:'X1 · 1 × 10⁻⁴ W/m²',effects:'Wide-area HF radio blackout for about an hour on the sunlit side; low-frequency navigation can degrade.'},
      {level:'R4',descriptor:'Severe',threshold:1e-3,thresholdLabel:'X10 · 1 × 10⁻³ W/m²',effects:'HF radio blackout across most of the sunlit side for 1–2 hours; navigation outages and minor satellite-navigation disruption are possible.'},
      {level:'R5',descriptor:'Extreme',threshold:2e-3,thresholdLabel:'X20 · 2 × 10⁻³ W/m²',effects:'HF radio blackout across the sunlit side for hours; satellite-navigation errors can rise and low-frequency navigation can be unavailable for hours.'},
    ],
  },
  geomagnetic: {
    key: 'geomagnetic', code: 'G', title: 'Geomagnetic storms', category: 'geomagnetic', measurementKey: 'kp',
    measurement: 'NOAA estimated planetary Kp index', unit: 'Kp', maxAgeMinutes: 360,
    baseline: 'Kp 0–4: below the NOAA G1 geomagnetic-storm threshold.',
    description: 'Kp summarizes global disturbances in Earth’s horizontal magnetic field over a three-hour interval. Local conditions can differ from a global index.',
    steps: [
      {level:'G1',descriptor:'Minor',threshold:5,thresholdLabel:'Kp = 5',effects:'Weak power-grid fluctuations can occur; minor satellite-operation impacts are possible.'},
      {level:'G2',descriptor:'Moderate',threshold:6,thresholdLabel:'Kp = 6',effects:'High-latitude power systems may see voltage alarms. Ground teams may need to correct spacecraft orientation; changing drag can affect orbit predictions.'},
      {level:'G3',descriptor:'Strong',threshold:7,thresholdLabel:'Kp = 7',effects:'Spacecraft surface charging and increased low-orbit drag may occur; orientation corrections may be needed. Intermittent satellite-navigation and radio problems are possible.'},
      {level:'G4',descriptor:'Severe',threshold:8,thresholdLabel:'Kp = 8 (including 9−)',effects:'Spacecraft may experience charging, tracking, and orientation problems. Satellite navigation can degrade for hours; power-grid voltage problems are possible.'},
      {level:'G5',descriptor:'Extreme',threshold:9,thresholdLabel:'Kp = 9',effects:'Extensive spacecraft charging, orientation, uplink/downlink, and tracking problems may occur. Satellite navigation may be degraded for days; severe grid effects are possible.'},
    ],
  },
  radiation: {
    key: 'radiation', code: 'S', title: 'Solar radiation storms', category: 'radiation', measurementKey: 'protons',
    measurement: 'GOES ≥10 MeV proton flux', unit: 'pfu', maxAgeMinutes: 30,
    baseline: 'Below 10 pfu: below the first NOAA S-scale threshold. This is not a claim of zero radiation.',
    description: 'The S-scale uses energetic protons measured by GOES at geostationary orbit. Actual dose depends on particle energy, shielding, spacecraft design, and orbit.',
    steps: [
      {level:'S1',descriptor:'Minor',threshold:10,thresholdLabel:'10 pfu',effects:'Minor HF-radio impacts in polar regions; NOAA lists no biological or satellite-operation effects at this level.'},
      {level:'S2',descriptor:'Moderate',threshold:100,thresholdLabel:'100 pfu',effects:'Infrequent single-event upsets in satellites are possible; polar radio and navigation may be affected. High-altitude polar flights may have elevated radiation exposure.'},
      {level:'S3',descriptor:'Strong',threshold:1000,thresholdLabel:'1,000 pfu',effects:'Single-event upsets, imaging noise, and slight solar-panel efficiency loss are likely. Radiation avoidance is recommended for astronaut spacewalks; polar navigation errors are likely.'},
      {level:'S4',descriptor:'Severe',threshold:10000,thresholdLabel:'10,000 pfu',effects:'Satellite memory or imaging problems and star-tracker/orientation issues may occur; solar-panel efficiency can degrade. Spacewalk radiation is hazardous and polar HF can black out.'},
      {level:'S5',descriptor:'Extreme',threshold:100000,thresholdLabel:'100,000 pfu',effects:'Severe satellite anomalies are possible, including loss of control or permanent solar-panel damage. Polar HF can black out and navigation can become extremely difficult.'},
    ],
  },
});

export const GLOSSARY = Object.freeze([
  {term:'X-ray flux',category:'sun',definition:'The rate of solar X-ray energy measured at Earth in a wavelength band; Solaris shows the GOES 0.1–0.8 nm band in watts per square metre.',keywords:['xrs','measurement','watts']},
  {term:'GOES XRS',category:'sun',definition:'The X-Ray Sensor on NOAA’s GOES spacecraft. It measures solar X-rays used to classify flare strength.',keywords:['satellite','sensor']},
  {term:'Solar flare class',category:'sun',definition:'A, B, C, M, and X classes group peak GOES X-ray flux in decade-wide ranges. Each letter step is ten times the previous one; the number is a multiplier.',keywords:['flare','a b c m x']},
  {term:'R-scale',category:'radio',definition:'NOAA’s radio-blackout scale. R1 begins at M1 X-ray flux; higher R levels describe progressively stronger possible sunlit-side radio/navigation effects.',keywords:['radio','blackout','x-ray']},
  {term:'HF radio',category:'radio',definition:'High-frequency radio, roughly 3–30 MHz, used for long-distance communications including aviation and maritime links.',keywords:['communications','frequency']},
  {term:'Kp index',category:'geomagnetic',definition:'A global, three-hour index of disturbances in Earth’s horizontal magnetic field. NOAA G1 begins at Kp 5.',keywords:['magnetic','geomagnetic','index']},
  {term:'Geomagnetic storm',category:'geomagnetic',definition:'A disturbance in Earth’s magnetic environment, often driven by solar-wind structures interacting with the magnetosphere.',keywords:['storm','magnetosphere']},
  {term:'Ionosphere',category:'geomagnetic',definition:'An electrically charged region of the upper atmosphere. Changes there can alter radio propagation and navigation-signal paths.',keywords:['atmosphere','radio','navigation']},
  {term:'Energetic protons',category:'radiation',definition:'Fast, positively charged particles from the Sun. Higher-energy particles can penetrate farther into spacecraft materials.',keywords:['particle','solar radiation','spacecraft']},
  {term:'Particle flux unit (pfu)',category:'radiation',definition:'A measure of particle flow: particles per square centimetre per second per steradian. NOAA’s S-scale uses ≥10 MeV proton flux.',keywords:['particle','unit','protons']},
  {term:'Single-event upset',category:'radiation',definition:'A temporary bit or logic change in electronics caused when one energetic particle deposits charge in a device.',keywords:['particle','electronics','satellite']},
  {term:'GNSS',category:'navigation',definition:'Global Navigation Satellite Systems, including GPS. Ionospheric changes can add signal delay or errors; impacts depend on location and receiver.',keywords:['navigation','GPS','position']},
  {term:'Calibrated probability',category:'model',definition:'The model’s estimated chance for its defined outcome, adjusted by its fitted probability calibrator. It is not certainty or a NOAA alert.',keywords:['probability','forecast','calibration']},
  {term:'Forecast threshold',category:'model',definition:'A chosen probability boundary for flagging a model output. Solaris V6 uses 0.20594365951619512 for its experimental forecast-alert flag.',keywords:['probability','alert','cutoff']},
  {term:'Risk band',category:'model',definition:'A Low, Moderate, or High label derived from V6 probability cutoffs 0.02756797277329327 and 0.36999108243721823; it is not an impact scale.',keywords:['risk','probability','classification']},
  {term:'Shadow mode',category:'model',definition:'A forecast is shown for observation and evaluation only; it does not issue an operational warning or control a spacecraft.',keywords:['experimental','operations']},
  {term:'UTC',category:'data',definition:'Coordinated Universal Time, the common time reference used for observations and timestamps in Solaris AI.',keywords:['time','timestamp']},
  {term:'Observed vs forecast',category:'data',definition:'An observation is a measured past or current value. A forecast is a model estimate about a later time window; the two should not be read as the same kind of evidence.',keywords:['measurement','prediction','data quality']},
]);

const numberOrNull = value => value === null || value === undefined || value === '' ? null : Number(value);

export function classifyScaleValue(scaleKey, value) {
  const scale = NOAA_SCALES[scaleKey];
  const number = numberOrNull(value);
  if (!scale || number === null || !Number.isFinite(number) || number < 0) return 'Unavailable';
  let reached = null;
  for (const step of scale.steps) if (number >= step.threshold) reached = step.level;
  return reached || `Below ${scale.steps[0].level}`;
}

export function classifyFlareClass(value) {
  const number = numberOrNull(value);
  if (number === null || !Number.isFinite(number) || number < 0) return 'Unavailable';
  let reached = null;
  for (const item of NOAA_SCALES.radio.flareClasses) if (number >= item.threshold) reached = item.letter;
  return reached || 'Unavailable';
}

export function classifyModelRisk(value) {
  const number = numberOrNull(value);
  if (number === null || !Number.isFinite(number) || number < 0 || number > 1) return 'Unavailable';
  if (number >= MODEL_THRESHOLDS.moderateHigh) return 'High';
  if (number >= MODEL_THRESHOLDS.lowModerate) return 'Moderate';
  return 'Low';
}

export function hasForecastAlert(value) {
  const number = numberOrNull(value);
  return number !== null && Number.isFinite(number) && number >= MODEL_THRESHOLDS.forecastAlert;
}

export function filterGlossary(query = '', category = 'all') {
  const needle = String(query).trim().toLowerCase();
  return GLOSSARY.filter(entry => (category === 'all' || entry.category === category) &&
    (!needle || [entry.term, entry.definition, ...entry.keywords].join(' ').toLowerCase().includes(needle)));
}

export function liveScaleReading(scaleKey, measurements = {}, now = Date.now()) {
  const scale = NOAA_SCALES[scaleKey];
  const observation = scale ? measurements?.[scale.measurementKey] : null;
  const value = numberOrNull(observation?.value);
  const rawTime = observation?.time;
  const observedAt = typeof rawTime === 'string' && /(?:Z|[+-]\d{2}:\d{2})$/i.test(rawTime) ? Date.parse(rawTime) : NaN;
  const nowMs = now instanceof Date ? now.getTime() : Number(now);
  if (!scale || value === null || !Number.isFinite(value) || value < 0 || !Number.isFinite(observedAt) ||
      !Number.isFinite(nowMs) || observedAt - nowMs > 5 * 60_000 || nowMs - observedAt > scale.maxAgeMinutes * 60_000) {
    return {status:'unavailable',level:'Unavailable',value:null,time:null};
  }
  return {status:'live',level:classifyScaleValue(scaleKey, value),value,time:new Date(observedAt).toISOString()};
}
