import numpy as np
import pandas as pd

def predict(bundle, features):
    """Calibrated Version 6 inference on already quality-checked features."""
    columns = bundle['feature_columns']
    if len(columns) != 38 or len(set(columns)) != 38 or list(features.index) != columns:
        raise ValueError('Feature schema/order does not match Version 6')
    values = pd.to_numeric(features, errors='raise').to_numpy(dtype=float)
    if np.isinf(values).any() or np.isnan(values).sum() > 3:
        raise ValueError('Invalid or excessive missing features')
    if any(not np.isfinite(features[c]) or features[c] < .8 for c in ('xrsa_coverage','xrsb_coverage','xrsa_coverage_roll24h_mean','xrsb_coverage_roll24h_mean')):
        raise ValueError('Insufficient quality coverage')
    frame = pd.DataFrame([values], columns=columns)
    raw = float(bundle['model'].predict_proba(frame)[0,1])
    if not np.isfinite(raw) or not 0 <= raw <= 1:
        raise ValueError('Invalid raw probability')
    clipped = np.clip(raw, 1e-6, 1-1e-6)
    prob = float(bundle['probability_calibrator'].predict_proba([[np.log(clipped/(1-clipped))]])[0,1])
    if not np.isfinite(prob) or not 0 <= prob <= 1:
        raise ValueError('Invalid calibrated probability')
    return prob
