"""Load the supplied Version 6 bundle and expose calibrated shadow inference."""
import csv
import hashlib
import json
from functools import lru_cache
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.ensemble import RandomForestClassifier
from inference import predict

ROOT = Path(__file__).parent / 'models'
MODEL = ROOT / 'solaris_ai_random_forest_phase2.joblib'
EXPECTED_SHA256 = '8dcb0d7d2fc7e3b2db89e0d48517bca6a5722763f6844790903c209bfe4b7b77'

@lru_cache(maxsize=1)
def load_bundle():
    # Only load the exact user-supplied model. Joblib uses pickle and may execute code.
    if sklearn.__version__ != '1.6.1':
        raise RuntimeError('Version 6 requires scikit-learn 1.6.1')
    if hashlib.sha256(MODEL.read_bytes()).hexdigest() != EXPECTED_SHA256:
        raise RuntimeError('Model file does not match the supplied Version 6 artifact')
    b = joblib.load(MODEL)
    schema = json.loads((ROOT / 'solaris_ai_feature_schema.json').read_text(encoding='utf8'))
    names = [row['name'] for row in schema['features']]
    if len(names) != 38 or len(set(names)) != 38 or b['feature_columns'] != names:
        raise RuntimeError('Version 6 feature schema mismatch')
    if not isinstance(b['model'].named_steps['model'], RandomForestClassifier):
        raise RuntimeError('Artifact is not the expected Random Forest pipeline')
    if abs(b['operating_threshold'] - 0.20594365951619512) > 1e-12 or abs(b['risk_cutoffs']['low_moderate'] - 0.02756797277329327) > 1e-12 or abs(b['risk_cutoffs']['moderate_high'] - 0.36999108243721823) > 1e-12:
        raise RuntimeError('Artifact thresholds do not match Version 6')
    return b

def model_details():
    b = load_bundle()
    with (ROOT / 'solaris_ai_phase2_model_comparison_descriptive_test.csv').open(encoding='utf8',newline='') as f:
        rows = list(csv.DictReader(f))
    row = next(r for r in rows if r['Model'] == 'Random Forest (optimized + calibrated)')
    return {'name':'Version 6 Random Forest','artifact_present':True,'artifact_verified':True,'mode':'shadow','feature_count':len(b['feature_columns']),'forecast_threshold':b['operating_threshold'],'risk_thresholds':b['risk_cutoffs'],
            'performance':{'period':'2020–2024','scope':'Historical descriptive test, hourly forecast windows','threshold':float(row['Threshold']),'accuracy':float(row['Accuracy']),'precision':float(row['Precision']),'recall':float(row['Recall']),'f1':float(row['F1']),'tss':float(row['TSS']),'roc_auc':float(row['ROC_AUC']),'pr_auc':float(row['PR_AUC']),'brier':float(row['Brier'])},
            'note':'Model loaded and checked. Live shadow forecasts use operational NOAA inputs; their equivalence to science-quality training data has not been validated.'}

def predict_features(values):
    b = load_bundle()
    names = b['feature_columns']
    if not isinstance(values, dict) or set(values) != set(names):
        raise ValueError('Feature schema must contain exactly the 38 Version 6 feature names')
    if any(v is not None and (isinstance(v, bool) or not isinstance(v, (int,float))) for v in values.values()):
        raise ValueError('All feature values must be numeric or null')
    features = pd.Series([values[c] for c in names], index=names, dtype=float)
    prob = predict(b, features)
    cut = b['risk_cutoffs']
    risk = 'Low' if prob < cut['low_moderate'] else 'Moderate' if prob < cut['moderate_high'] else 'High'
    bounds = b['feature_value_monitoring_bounds_0_1pct']
    out_of_range = [c for c in names if np.isfinite(features[c]) and (features[c] < bounds['lower'][c] or features[c] > bounds['upper'][c])]
    return {'status':'available','mode':'shadow','probability':prob,'risk':risk,'alert':prob >= b['operating_threshold'],'threshold':b['operating_threshold'],'horizon_hours':24,'out_of_range_features':out_of_range,'missing_features':features[features.isna()].index.tolist(),'note':'Result uses caller-supplied features; data origin, timing and quality have not been independently verified.'}
