"""Experimental SWPC operational XRS adapter; science-quality flags unavailable."""
import math
import numpy as np
import pandas as pd
from features import summarize_features

def operational_features(records, now):
    now = pd.Timestamp(now)
    if now.tz is None:
        raise ValueError('Current time must be UTC-aware')
    now = now.tz_convert('UTC')
    timestamp = now.floor('h')
    start = timestamp - pd.Timedelta(hours=72)
    bands = {'0.05-0.4nm':'xrsa', '0.1-0.8nm':'xrsb'}
    rows = pd.DataFrame.from_records(records)
    needed = {'time_tag','energy','flux','satellite'}
    if not needed.issubset(rows.columns): raise ValueError('Insufficient X-ray observation coverage')
    rows = rows.loc[rows['energy'].isin(bands), ['time_tag','energy','flux','satellite']].copy()
    rows['time'] = pd.to_datetime(rows['time_tag'], utc=True, errors='coerce', format='mixed')
    rows['band'] = rows['energy'].map(bands)
    rows['flux'] = pd.to_numeric(rows['flux'], errors='coerce')
    rows = rows.loc[rows['time'].notna() & (rows['time'] >= start) & (rows['time'] <= now + pd.Timedelta(minutes=5)) & (rows['time'] == rows['time'].dt.floor('min')) & np.isfinite(rows['flux']) & (rows['flux'] > 0), ['time','band','flux','satellite']]
    if rows.empty: raise ValueError('Insufficient X-ray observation coverage')
    for band in bands.values():
        latest = rows[rows['band'] == band]['time'].max()
        if pd.isna(latest): raise ValueError(f'Insufficient {band} observation coverage')
        if now - latest > pd.Timedelta(minutes=15): raise ValueError(f'{band} observations are stale')
    prior = rows[rows['time'] < timestamp]
    if prior.duplicated(['time','band']).any(): raise ValueError('Duplicate NOAA measurements')
    satellites = prior['satellite'].dropna().unique()
    if len(satellites) != 1 or prior['satellite'].isna().any(): raise ValueError('Multiple or unknown GOES satellites in the input window')
    index = pd.date_range(start,timestamp-pd.Timedelta(minutes=1),freq='min')
    matrix = prior.pivot(index='time',columns='band',values='flux').reindex(index)
    transformed = pd.DataFrame(index=index)
    coverage = {}
    for band in bands.values():
        series = matrix[band] if band in matrix else pd.Series(np.nan,index=index)
        valid = np.isfinite(series) & (series > 0)
        for hours in (1,24,72):
            fraction = float(valid.iloc[-hours*60:].sum()) / (hours*60)
            coverage[f'{band}_{hours}h'] = fraction
            if fraction < .8: raise ValueError(f'Insufficient {band} observation coverage in {hours}h window')
        transformed[band+'_log'] = np.log10(series.clip(lower=1e-12)).where(valid)
        transformed[band+'_ok'] = valid.astype('float32')
    features = summarize_features(transformed,timestamp)
    return features, {'forecast_time':timestamp.isoformat(),'observations_through':str(prior['time'].max().isoformat()),'feed_latest':str(rows['time'].max().isoformat()),'satellite':str(satellites[0]),'coverage':coverage,'science_quality_flags_available':False}
