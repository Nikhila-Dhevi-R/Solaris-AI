# Solaris AI Phase 2 deployment guide

## Artifacts and contract
Load solaris_ai_random_forest_phase2.joblib. It contains the fitted median imputer + Random Forest sklearn pipeline, frozen logistic probability calibrator, exact ordered 38-feature schema, default warning threshold, risk cutoffs, and historical range-monitor bounds. solaris_ai_feature_schema.json is the machine-readable input contract; solaris_ai_phase2_thresholds.json is the threshold config.

Use the frozen 0.205944 cutoff for the default binary warning. Risk bands were selected on 2017 validation only. They are operational tiers, not guaranteed calibrated probabilities under later solar-cycle drift.

## Generate the required features
1. Read NOAA GOES XRS-A/XRS-B one-minute science-quality flux (underlying units W m^-2); reject flagged, fill-valued, non-finite, eclipse/interpolated/bad-quality measurements using the same V5 rules.
2. Convert timestamps to UTC. For forecast time t, use only completed hourly bins ending before t; never include an hour still in progress or any post-t observation.
3. Reproduce the V5 log transform exactly. Per band, calculate hourly log-flux mean, maximum, standard deviation, and observation coverage.
4. Reproduce the V5 trailing 6h/24h/72h means and maxima for log-flux statistics, plus trailing 24h mean coverage. Use only past completed bins.
5. Add hour_sin, hour_cos, annual_sin, and annual_cos from the UTC forecast timestamp. Keep exact feature names and order in the JSON schema. Flux-derived values must follow the V5 transform; coverage is a fraction and calendar encodings are dimensionless.
6. Build one numeric row with exactly 38 features in schema order. NaN measurements are permitted and handled by the fitted median imputer; reject absent/extra/reordered fields, nonnumeric values, and infinities. Monitor values outside the bundled historical 0.1%-99.9% range.

## FastAPI inference pattern
The following is the core inference function; place it behind a POST endpoint and map validation errors to HTTP 422.

    from pathlib import Path
    import joblib, numpy as np, pandas as pd
    from fastapi import FastAPI, HTTPException

    app = FastAPI()
    bundle = joblib.load(Path('/models/solaris_ai_random_forest_phase2.joblib'))
    features = bundle['feature_columns']

    def infer(payload: dict):
        if list(payload.keys()) != features:
            raise ValueError('Expected exactly 38 features in schema order')
        row = pd.DataFrame([[payload[k] for k in features]], columns=features)
        if any(not pd.api.types.is_numeric_dtype(row[c]) for c in features):
            raise ValueError('Features must be numeric')
        x = row.to_numpy(dtype=float)
        if np.isinf(x).any():
            raise ValueError('Infinite features are invalid')
        raw = bundle['model'].predict_proba(row)[:, 1]
        raw = np.clip(raw, 1e-6, 1 - 1e-6)
        logit = np.log(raw / (1 - raw)).reshape(-1, 1)
        p = float(bundle['probability_calibrator'].predict_proba(logit)[0, 1])
        low = bundle['risk_cutoffs']['low_moderate']
        high = bundle['risk_cutoffs']['moderate_high']
        risk = 'Low' if p < low else ('Moderate' if p < high else 'High')
        return {'probability': p, 'forecast_alert': p >= bundle['operating_threshold'], 'risk_level': risk}

    @app.post('/forecast')
    def forecast(payload: dict):
        try:
            return infer(payload)
        except (TypeError, ValueError) as exc:
            raise HTTPException(status_code=422, detail=str(exc))

Keep feature construction in a tested UTC feature service and pass its output to inference. The joblib pipeline handles missing-value imputation and Random Forest prediction; the bundled calibrator maps raw RF scores to the deployment probability.

## Monitoring and limits
Record probability, input coverage, range-monitor flags, model version, and forecast timestamp. Review calibration and alert volume on a new chronologically held-out period before changing calibration or thresholds. Do not use the already-observed 2020-2024 results to retune. The provided labels have hourly forecast timestamps but no flare onset/peak catalog; event lead times and event-matched false-alert episodes are not computed.
