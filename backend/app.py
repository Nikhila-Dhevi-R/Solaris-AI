from __future__ import annotations

import asyncio
import logging
import math
import os
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from model_service import model_details, predict_features
from realtime import operational_features

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('solaris')
app = FastAPI(title='Solaris AI', version='1.0.0')
app.add_middleware(CORSMiddleware, allow_origins=['http://localhost:5173', 'http://127.0.0.1:5173'], allow_methods=['GET'], allow_headers=['*'])
BASE = 'https://services.swpc.noaa.gov'
MODEL = Path(__file__).parent / 'models' / 'solaris_ai_random_forest_phase2.joblib'
_cache = {}

async def get_noaa(path: str, ttl: int = 120):
    now = time.monotonic()
    if path in _cache and now - _cache[path][0] < ttl:
        return _cache[path][1]
    try:
        async with httpx.AsyncClient(timeout=25, follow_redirects=True) as client:
            for attempt in range(2):
                response = await client.get(BASE + path)
                response.raise_for_status()
                try:
                    data = response.json()
                    if not isinstance(data, list) or not data:
                        raise ValueError('empty or invalid response')
                    break
                except ValueError:
                    if attempt: raise
                    await asyncio.sleep(0.5)
        _cache[path] = (now, data)
        return data
    except (httpx.HTTPError, ValueError) as exc:
        log.warning('NOAA request failed for %s: %s', path, exc)
        raise HTTPException(503, 'NOAA data temporarily unavailable') from exc

def classify_risk(probability):
    if not 0 <= probability <= 1:
        raise ValueError('Probability must be between 0 and 1')
    return 'Low' if probability < .027568 else 'Moderate' if probability < .369991 else 'High'

def flare_class(flux):
    if flux is None or not math.isfinite(flux) or flux <= 0:
        return None
    for label, scale in [('X',1e-4),('M',1e-5),('C',1e-6),('B',1e-7),('A',1e-8)]:
        if flux >= scale:
            return f'{label}{flux / scale:.1f}'
    return f'A{flux / 1e-8:.2f}'

def forecast_status():
    reason = ('Version 6 artifact is missing.' if not MODEL.is_file() else 'Real-time NOAA feed quality flags have not been validated against the science-quality data used to train Version 6.')
    return {'status':'unavailable','probability':None,'risk':None,'alert':None,'mode':'shadow','reason':reason,'horizon_hours':24}

@app.get('/api/health')
def health():
    return {'status':'ok','mode':'shadow'}

@app.get('/api/forecast')
async def forecast():
    try:
        records = await get_noaa('/json/goes/primary/xrays-7-day.json')
        features, quality = await asyncio.to_thread(operational_features, records, datetime.now(timezone.utc))
        result = await asyncio.to_thread(predict_features, features.to_dict())
        result.update(quality)
        result['source'] = 'NOAA SWPC operational GOES XRS'
        result['experimental'] = True
        result['note'] = ('Experimental shadow forecast from operational NOAA flux. The feed lacks the science-quality flags used in training; equivalence and real-time accuracy have not been validated. Not an operational warning.')
        return result
    except HTTPException:
        return {**forecast_status(), 'reason':'NOAA observations are unavailable.'}
    except ValueError as exc:
        return {**forecast_status(), 'reason':str(exc)}
    except Exception:
        log.exception('Experimental forecast failed')
        return {**forecast_status(), 'reason':'Model inference unavailable; check backend logs.'}

@app.get('/api/model')
def model():
    try:
        return model_details()
    except Exception:
        log.exception('Model could not be loaded')
        return {'name':'Version 6 Random Forest','artifact_present':MODEL.is_file(),'artifact_verified':False,'performance':None,'mode':'shadow','note':'Model could not be verified; check backend logs and dependencies.'}

class FeatureInput(BaseModel):
    features: dict[str, float | None]

@app.post('/api/forecast/features')
def forecast_features(payload: FeatureInput):
    try:
        return predict_features(payload.features)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    except Exception as exc:
        log.exception('Model inference unavailable')
        raise HTTPException(503, 'Model inference unavailable; check backend logs') from exc

@app.get('/api/conditions')
async def conditions():
    data = await get_noaa('/json/goes/primary/xrays-6-hour.json')
    rows = [r for r in data if r.get('energy') == '0.1-0.8nm' and isinstance(r.get('flux'), (int,float)) and math.isfinite(r['flux']) and r['flux'] > 0 and r.get('time_tag')]
    if not rows: raise HTTPException(503, 'No valid X-ray observations')
    row = max(rows, key=lambda r:r['time_tag'])
    try:
        observed = datetime.fromisoformat(row['time_tag'].replace('Z','+00:00'))
        age = (datetime.now(timezone.utc) - observed).total_seconds()
    except (ValueError, TypeError): raise HTTPException(503, 'Invalid NOAA observation timestamp')
    return {'status':'stale' if age > 900 or age < -300 else 'live','time':row['time_tag'],'satellite':row.get('satellite'),'flux':row['flux'],'class':flare_class(row['flux']),'age_seconds':round(age),'source':'NOAA SWPC GOES primary XRS, 0.1–0.8 nm','quality_note':'Real-time observations; quality and revisions may differ from science-quality archives.'}

@app.get('/api/history')
async def history(hours: int = Query(24, ge=1, le=168)):
    data = await get_noaa('/json/goes/primary/xrays-7-day.json')
    rows = [r for r in data if r.get('energy') == '0.1-0.8nm' and isinstance(r.get('flux'),(int,float)) and math.isfinite(r['flux']) and r['flux'] > 0 and r.get('time_tag')]
    rows.sort(key=lambda x:x['time_tag'])
    if not rows: raise HTTPException(503,'No valid X-ray observations')
    # NOAA's native one-minute readings are downsampled for display only.
    try:
        cutoff = datetime.fromisoformat(rows[-1]['time_tag'].replace('Z','+00:00')) - timedelta(hours=hours)
        rows = [r for r in rows if datetime.fromisoformat(r['time_tag'].replace('Z','+00:00')) >= cutoff]
    except (ValueError, TypeError):
        raise HTTPException(503, 'Invalid NOAA history timestamps')
    step = max(1, len(rows)//400)
    return {'source':'NOAA SWPC GOES primary XRS','points':[{'time':r['time_tag'],'flux':r['flux']} for r in rows[::step]],'hours_requested':hours}

@app.get('/api/alerts')
async def alerts():
    data = await get_noaa('/products/alerts.json', 300)
    data = sorted(data, key=lambda r:r.get('issue_datetime',''), reverse=True)
    return {'source':'NOAA SWPC','items':data[:15], 'note':'Recent issued products; not necessarily active alerts.'}

@app.get('/api/satellites')
def satellites():
    return {'status':'unavailable','items':[],'reason':'Orbital elements and satellite-specific impact models are not configured. Spacecraft impacts cannot be inferred from X-rays alone.','recommendation':'Consult current NOAA alerts and mission-specific procedures; do not use this display for autonomous decisions.'}
