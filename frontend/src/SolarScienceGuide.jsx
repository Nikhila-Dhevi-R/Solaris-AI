import React, {useMemo, useState} from 'react';
import {Activity, ArrowLeft, BookOpen, CircleHelp, ExternalLink, Search, Shield, Sun, Waves, Zap} from 'lucide-react';
import {classifyFlareClass, filterGlossary, liveScaleReading, MODEL_THRESHOLDS, NOAA_SCALES} from './solarGuideData.js';

const scaleOrder = ['radio','geomagnetic','radiation'];
const categories = [
  ['all','All terms'],['sun','The Sun'],['radio','Radio'],['geomagnetic','Geomagnetic'],
  ['radiation','Radiation'],['navigation','Navigation'],['model','Model'],['data','Data & time'],
];
const scaleIcons = {radio:Waves,geomagnetic:Activity,radiation:Zap};
const utc = value => value ? new Date(value).toLocaleString('en-GB',{timeZone:'UTC',day:'2-digit',month:'short',hour:'2-digit',minute:'2-digit'})+' UTC' : 'Time unavailable';
const fixed = (value, scaleKey) => scaleKey === 'radio' ? `${Number(value).toExponential(2)} W/m²` : scaleKey === 'geomagnetic' ? `Kp ${Number(value).toFixed(1)}` : `${Number(value).toLocaleString('en-US',{maximumFractionDigits:1})} pfu`;

function LiveMeasurement({scaleKey,measurements}) {
  const scale = NOAA_SCALES[scaleKey];
  const reading = liveScaleReading(scaleKey, measurements);
  const Icon = scaleIcons[scaleKey];
  return <article className={`live-measurement ${reading.status==='live'?'is-live':'is-unavailable'}`}>
    <div className="live-measurement-top"><span><Icon size={16}/>{scale.measurement}</span><i>{reading.status==='live'?'LIVE':'UNAVAILABLE'}</i></div>
    <strong>{reading.status==='live'?fixed(reading.value,scaleKey):'—'}</strong>
    <div className="live-measurement-bottom"><span>{reading.level==='Unavailable'?'Waiting for a fresh measurement':reading.level==='Below '+scale.steps[0].level?'Below first NOAA level':`${reading.level} threshold reached`}</span><small>{reading.status==='live'?utc(reading.time):'NOAA feed missing or stale'}</small></div>
  </article>;
}

export default function SolarScienceGuide({conditions,satellites,forecast,model,onBack}) {
  const [scaleKey,setScaleKey]=useState('radio');
  const [query,setQuery]=useState('');
  const [category,setCategory]=useState('all');
  const scale=NOAA_SCALES[scaleKey];
  const selectedReading=liveScaleReading(scaleKey,satellites?.measurements);
  const glossary=useMemo(()=>filterGlossary(query,category),[query,category]);
  const activeLevel=selectedReading.status==='live'?selectedReading.level:null;
  const probability=forecast?.status==='available'&&Number.isFinite(forecast.probability)?forecast.probability:null;
  const modelRisk=probability===null?'Unavailable':forecast.risk;
  const xrayClass=conditions?.class;

  return <div className="solar-guide-page">
    <section className="guide-hero">
      <div className="guide-hero-copy">
        <div className="guide-kicker"><Sun size={15}/> SOLAR WEATHER FIELD GUIDE</div>
        <h2>Space weather,<br/><em>in plain language.</em></h2>
        <p>Learn what the measurements mean, where NOAA’s alert scales begin, and what may change as conditions rise.</p>
        <button className="guide-back" onClick={onBack}><ArrowLeft size={15}/> Back to V6 model</button>
      </div>
      <div className="guide-sun-art" aria-hidden="true"><div className="guide-sun-orbit orbit-a"/><div className="guide-sun-orbit orbit-b"/><div className="guide-sun-core"/><span>OBSERVE · UNDERSTAND</span></div>
      <div className="guide-hero-caption">MEASURED CONDITIONS <b>≠</b> MODEL FORECAST</div>
    </section>

    <section className="guide-live-section" aria-labelledby="live-weather-title">
      <div className="guide-section-heading"><div><div className="eyebrow muted">FROM THE CONNECTED NOAA FEEDS</div><h3 id="live-weather-title">What is happening now?</h3><p>Measured values are shown only when a fresh observation is available.</p></div><span className="guide-live-tag"><i/> OBSERVATIONS</span></div>
      <div className="guide-live-grid">{scaleOrder.map(key=><LiveMeasurement key={key} scaleKey={key} measurements={satellites?.measurements}/>)}</div>
      <div className="guide-callout"><CircleHelp size={17}/><p><strong>Reading the status</strong> “Below first NOAA level” means the measurement is below that scale’s first named threshold. “Unavailable” means this page could not confirm a sufficiently recent value.</p></div>
    </section>

    <section className="guide-scale-section" aria-labelledby="scales-title">
      <div className="guide-section-heading"><div><div className="eyebrow muted">THRESHOLD ATLAS</div><h3 id="scales-title">What changes as a threshold is crossed?</h3><p>These NOAA scales describe possible environmental effects. They are not predictions of a particular satellite failure.</p></div><span className="scale-count">03 SCALE FAMILIES</span></div>
      <div className="scale-tabs" role="tablist" aria-label="NOAA space-weather scales">
        {scaleOrder.map(key=>{const item=NOAA_SCALES[key];const Icon=scaleIcons[key];return <button key={key} role="tab" aria-selected={scaleKey===key} className={scaleKey===key?'selected':''} onClick={()=>setScaleKey(key)}><Icon size={16}/><span>{item.code}-scale</span></button>;})}
      </div>
      <div className="scale-intro"><div><span className="scale-code">{scale.code}</span><div><h4>{scale.title}</h4><p>{scale.description}</p></div></div><div className="scale-live-value"><small>CURRENT CLASSIFICATION</small><strong>{selectedReading.status==='live'?selectedReading.level:'Unavailable'}</strong><span>{selectedReading.status==='live'?fixed(selectedReading.value,scaleKey):'Waiting for fresh data'}</span></div></div>
      <div className="scale-baseline"><span>BASELINE</span><p>{scale.baseline}</p></div>
      {scaleKey==='radio'&&<div className="flare-class-section"><div className="flare-class-heading"><span>GOES FLARE CLASS</span><p>Each letter spans a tenfold flux range; the number after it is the multiplier (for example, M2 means 2 × 10⁻⁵ W/m²).</p></div><div className="flare-class-grid">{scale.flareClasses.map(item=><article key={item.letter} className={selectedReading.status==='live'&&classifyFlareClass(selectedReading.value)===item.letter?'current':''}><div><b>{item.letter}</b><strong>{item.range}</strong></div><p>{item.meaning}</p></article>)}</div></div>}
      <div className="scale-levels">{scale.steps.map((step,index)=><article key={step.level} className={`scale-level ${activeLevel===step.level?'current':''}`}>
        <div className="scale-level-meter"><span>{step.level}</span><i style={{'--level-index':index}}/></div>
        <div className="scale-level-content"><div className="scale-level-heading"><h5>{step.descriptor}</h5><b>{step.thresholdLabel}</b></div><p>{step.effects}</p></div>
        {activeLevel===step.level&&<span className="current-level-tag">CURRENTLY AT THIS LEVEL</span>}
      </article>)}</div>
      <p className="scale-caveat">The scale indicates broad, possible effects; local conditions, duration, latitude, orbit, shielding, and spacecraft design all matter. A scale crossing does not mean every system will be affected.</p>
      <div className="guide-sources"><strong>NOAA references</strong><a href="https://www.swpc.noaa.gov/noaa-scales-explanation" target="_blank" rel="noreferrer">Space Weather Scales <ExternalLink size={12}/></a><a href="https://www.spaceweather.gov/products/planetary-k-index" target="_blank" rel="noreferrer">Planetary Kp index <ExternalLink size={12}/></a><a href="https://www.spaceweather.gov/products/goes-proton-flux" target="_blank" rel="noreferrer">GOES proton flux <ExternalLink size={12}/></a></div>
    </section>

    <section className="model-threshold-card" aria-labelledby="v6-thresholds-title">
      <div className="model-threshold-heading"><div className="threshold-icon"><Shield size={19}/></div><div><div className="eyebrow muted">SEPARATE FROM THE NOAA SCALES</div><h3 id="v6-thresholds-title">How the Version 6 forecast is labeled</h3></div><span className="mini-badge">V6 · SHADOW MODE</span></div>
      <p className="model-threshold-intro">The Random Forest estimates the chance of at least one M- or X-class flare in a 24-hour window. These are frozen probability cutoffs chosen during model validation; they do not describe measured solar conditions or satellite impact.</p>
      <div className="model-live-probability"><div><small>CURRENT MODEL OUTPUT</small><strong>{probability===null?'Unavailable':`${(probability*100).toFixed(1)}%`}</strong><span>{probability===null?'The forecast is unavailable or input checks did not pass':`${modelRisk} model risk band · 24-hour horizon`}</span></div><div className="probability-rail"><i style={{width:probability===null?'0%':`${Math.max(2,Math.min(100,probability*100))}%`}}/></div></div>
      <div className="v6-threshold-grid"><article><span>LOW</span><strong>p &lt; {MODEL_THRESHOLDS.lowModerate.toFixed(6)}</strong><small>Full cutoff: {MODEL_THRESHOLDS.lowModerate}</small><p>Below the frozen Low/Moderate boundary.</p></article><article><span>MODERATE</span><strong>{MODEL_THRESHOLDS.lowModerate.toFixed(6)} ≤ p &lt; {MODEL_THRESHOLDS.moderateHigh.toFixed(6)}</strong><small>Full cutoffs: {MODEL_THRESHOLDS.lowModerate} / {MODEL_THRESHOLDS.moderateHigh}</small><p>Between the two validation-derived risk boundaries.</p></article><article><span>HIGH</span><strong>p ≥ {MODEL_THRESHOLDS.moderateHigh.toFixed(6)}</strong><small>Full cutoff: {MODEL_THRESHOLDS.moderateHigh}</small><p>At or above the frozen Moderate/High boundary.</p></article><article className="forecast-alert-threshold"><span>FORECAST ALERT FLAG</span><strong>p ≥ {MODEL_THRESHOLDS.forecastAlert.toFixed(6)}</strong><small>Full cutoff: {MODEL_THRESHOLDS.forecastAlert}</small><p>A separate binary flag; it can fall inside the Moderate band.</p></article></div>
      <div className="guide-callout"><CircleHelp size={17}/><p><strong>Why can the labels differ?</strong> The V6 risk band and forecast-alert flag use different validation cutoffs. Both describe model probability, not NOAA R/G/S conditions. This forecast remains experimental shadow information, not an operational warning.</p></div>
      {model?.performance&&<p className="model-context">The supplied historical evaluation covers {model.performance.period}; it does not establish real-time reliability on today’s live data.</p>}
    </section>

    <section className="glossary-section" aria-labelledby="glossary-title">
      <div className="guide-section-heading"><div><div className="eyebrow muted">THE SPACE WEATHER DICTIONARY</div><h3 id="glossary-title"><BookOpen size={20}/> Terms worth knowing</h3><p>Search the terms that appear throughout Solaris AI.</p></div><span className="scale-count">{glossary.length} {glossary.length===1?'TERM':'TERMS'}</span></div>
      <label className="glossary-search"><Search size={17}/><input value={query} onChange={event=>setQuery(event.target.value)} placeholder="Search a term, measurement, or acronym…" aria-label="Search glossary"/>{query&&<button onClick={()=>setQuery('')} aria-label="Clear search">Clear</button>}</label>
      <div className="glossary-filters" aria-label="Filter glossary by category">{categories.map(([key,label])=><button key={key} className={category===key?'selected':''} aria-pressed={category===key} onClick={()=>setCategory(key)}>{label}</button>)}</div>
      {glossary.length?<div className="glossary-grid">{glossary.map(entry=><article className="glossary-term" key={entry.term}><div><span>{categories.find(([key])=>key===entry.category)?.[1]||'Space weather'}</span><i>✦</i></div><h4>{entry.term}</h4><p>{entry.definition}</p></article>)}</div>:<div className="glossary-empty"><BookOpen size={20}/><strong>No matching terms yet</strong><span>Try another word or clear the selected filters.</span><button onClick={()=>{setQuery('');setCategory('all');}}>Reset glossary</button></div>}
      <div className="guide-sources glossary-source"><strong>NOAA glossary</strong><a href="https://www.spaceweather.gov/content/space-weather-glossary" target="_blank" rel="noreferrer">Explore the full NOAA glossary <ExternalLink size={12}/></a></div>
    </section>

    <div className="guide-footer-note"><CircleHelp size={17}/><p>Solaris AI is an informational research dashboard. Its V6 forecast is not operationally validated; use current NOAA products and mission-specific procedures for decisions.</p></div>
  </div>;
}
