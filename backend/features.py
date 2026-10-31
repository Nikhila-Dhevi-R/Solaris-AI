"""Version 6 science-quality XRS feature transformation, from its source notebook.

The live SWPC JSON is intentionally not passed here: it lacks the training
archive's per-band science quality flags.
"""
import numpy as np
import pandas as pd

def build_features(minute, timestamp):
    required = {'xrsa_flux','xrsb_flux','xrsa_flag','xrsb_flag'}
    if not required.issubset(minute.columns):
        raise ValueError('Science-quality flux and quality flags required for both bands')
    if not isinstance(minute.index, pd.DatetimeIndex) or minute.index.tz is None:
        raise ValueError('Measurements require timezone-aware timestamps')
    timestamp = pd.Timestamp(timestamp)
    if timestamp.tz is None or timestamp != timestamp.floor('h'):
        raise ValueError('Forecast timestamp must be an exact timezone-aware hour')
    timestamp = timestamp.tz_convert('UTC')
    minute = minute.copy()
    minute.index = minute.index.tz_convert('UTC')
    minute = minute[(minute.index >= timestamp - pd.Timedelta(hours=72)) & (minute.index < timestamp)].sort_index()
    if minute.index.has_duplicates or minute.empty:
        raise ValueError('Missing or duplicate observations')
    if any(minute.index != minute.index.floor('min')):
        raise ValueError('Observations must be minute-aligned')
    for hours in (1, 24, 72):
        window = minute[minute.index >= timestamp - pd.Timedelta(hours=hours)]
        if len(window) < 0.8 * hours * 60:
            raise ValueError(f'Insufficient observation coverage in {hours}h window')
    transformed = pd.DataFrame(index=minute.index)
    for band in ('xrsa','xrsb'):
        flux = pd.to_numeric(minute[band+'_flux'], errors='coerce')
        flag = pd.to_numeric(minute[band+'_flag'], errors='coerce')
        valid = np.isfinite(flux) & (flux > 0) & np.isfinite(flag) & (flag == 0)
        transformed[band+'_log'] = np.log10(flux.clip(lower=1e-12)).where(valid)
        transformed[band+'_ok'] = valid.astype('float32')
    return summarize_features(transformed, timestamp)

def summarize_features(transformed, timestamp):
    """Apply the Version 6 hourly and trailing transforms to prevalidated data."""
    h = transformed.resample('1h',closed='left',label='right').agg({'xrsa_log':['mean','max','std'],'xrsa_ok':'mean','xrsb_log':['mean','max','std'],'xrsb_ok':'mean'})
    h.columns = [f'{a}_{b}' for a,b in h.columns]
    h = h.rename(columns={'xrsa_ok_mean':'xrsa_coverage','xrsb_ok_mean':'xrsb_coverage'})
    h = h.reindex(pd.date_range(timestamp-pd.Timedelta(hours=71), timestamp, freq='h'))
    base = ['xrsa_log_mean','xrsa_log_max','xrsb_log_mean','xrsb_log_max']
    for window in (6,24,72):
        roll = h[base].rolling(window=window,min_periods=max(1,window//2))
        for col in base:
            h[f'{col}_roll{window}h_mean'] = roll[col].mean()
            h[f'{col}_roll{window}h_max'] = roll[col].max()
    for col in ('xrsa_coverage','xrsb_coverage'):
        h[f'{col}_roll24h_mean'] = h[col].rolling(24,min_periods=12).mean()
    idx=h.index
    h['hour_sin']=np.sin(2*np.pi*idx.hour/24)
    h['hour_cos']=np.cos(2*np.pi*idx.hour/24)
    phase=(idx.day_of_year-1)/365.25*2*np.pi
    h['annual_sin']=np.sin(phase)
    h['annual_cos']=np.cos(phase)
    return h.iloc[-1]
