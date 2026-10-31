from app import classify_risk, flare_class, forecast_status

def test_risk_threshold_boundaries():
    assert classify_risk(0.027567) == 'Low'
    assert classify_risk(0.027568) == 'Moderate'
    assert classify_risk(0.369991) == 'High'

def test_measured_flux_classification():
    assert flare_class(1e-5) == 'M1.0'
    assert flare_class(None) is None

def test_forecast_refuses_missing_model():
    result = forecast_status()
    assert result['status'] == 'unavailable'
    assert result['probability'] is None
    assert result['mode'] == 'shadow'

def test_feature_builder_uses_completed_hour_only():
    import pandas as pd
    from features import build_features
    idx = pd.date_range('2026-01-01', periods=73*60, freq='min', tz='UTC')
    frame = pd.DataFrame({'xrsa_flux':1e-8,'xrsb_flux':1e-6,'xrsa_flag':0,'xrsb_flag':0}, index=idx)
    frame.loc[idx[-1], 'xrsb_flux'] = 1e-2
    features = build_features(frame, pd.Timestamp('2026-01-04 00:00', tz='UTC'))
    assert len(features) == 38
    assert features['xrsb_log_max'] == -6
    assert features['xrsb_coverage'] == 1

def test_features_reject_unqualified_feed():
    import pandas as pd
    import pytest
    from features import build_features
    with pytest.raises(ValueError, match='quality flags'):
        build_features(pd.DataFrame(), pd.Timestamp('2026-01-01', tz='UTC'))

def test_api_reports_unavailable_forecast(monkeypatch):
    from fastapi.testclient import TestClient
    from app import app
    import app as app_module
    from fastapi import HTTPException
    async def unavailable(*args, **kwargs): raise HTTPException(503, 'Offline')
    monkeypatch.setattr(app_module, 'get_noaa', unavailable)
    client=TestClient(app)
    response=client.get('/api/forecast')
    assert response.status_code == 200
    assert response.json()['probability'] is None
    assert response.json()['mode'] == 'shadow'

def test_history_rejects_invalid_window():
    from fastapi.testclient import TestClient
    from app import app
    assert TestClient(app).get('/api/history?hours=999').status_code == 422

def test_model_bundle_load_and_metrics():
    from model_service import load_bundle, model_details
    bundle = load_bundle()
    assert len(bundle['feature_columns']) == 38
    assert abs(bundle['operating_threshold'] - 0.20594365951619512) < 1e-14
    details = model_details()
    assert details['artifact_verified'] is True
    assert abs(details['performance']['accuracy'] - 0.7921227878124429) < 1e-12
    assert details['performance']['period'] == '2020–2024'

def test_calibrated_model_forecast_from_feature_values():
    import pandas as pd
    from model_service import load_bundle, predict_features
    b = load_bundle()
    lo, hi = b['feature_value_monitoring_bounds_0_1pct']['lower'], b['feature_value_monitoring_bounds_0_1pct']['upper']
    values = {c: (float(lo[c]) + float(hi[c]))/2 for c in b['feature_columns']}
    for c in ('xrsa_coverage','xrsb_coverage','xrsa_coverage_roll24h_mean','xrsb_coverage_roll24h_mean'): values[c] = 1.0
    result = predict_features(values)
    assert 0 <= result['probability'] <= 1
    assert result['risk'] in ('Low','Moderate','High')
    assert result['mode'] == 'shadow'
    assert result['alert'] == (result['probability'] >= b['operating_threshold'])

def test_forecast_features_rejects_wrong_schema():
    import pytest
    from model_service import predict_features
    with pytest.raises(ValueError, match='schema'):
        predict_features({'not_a_feature': 3})

def test_sparse_minutes_rejected():
    import pandas as pd
    import pytest
    from features import build_features
    idx = pd.date_range('2026-01-01', periods=72, freq='h', tz='UTC')
    frame = pd.DataFrame({'xrsa_flux':1e-8,'xrsb_flux':1e-6,'xrsa_flag':0,'xrsb_flag':0}, index=idx)
    with pytest.raises(ValueError, match='coverage'):
        build_features(frame, pd.Timestamp('2026-01-04', tz='UTC'))

def test_feature_endpoint_rejects_invalid_payload():
    from fastapi.testclient import TestClient
    from app import app
    response = TestClient(app).post('/api/forecast/features', json={'features':{'wrong': 1}})
    assert response.status_code == 422

def operational_sample():
    import pandas as pd
    times=pd.date_range('2026-01-01',periods=72*60+1,freq='min',tz='UTC')
    return [{'time_tag':t.isoformat(),'energy':band,'flux':flux,'satellite':18} for t in times for band,flux in [('0.05-0.4nm',1e-8),('0.1-0.8nm',1e-6)]]

def test_operational_features_equal_training_transform_for_complete_valid_data():
    import pandas as pd
    from realtime import operational_features
    from features import build_features
    now=pd.Timestamp('2026-01-04T00:00:00Z')
    features,meta=operational_features(operational_sample(),now)
    idx=pd.date_range('2026-01-01',periods=72*60,freq='min',tz='UTC')
    science=pd.DataFrame({'xrsa_flux':1e-8,'xrsb_flux':1e-6,'xrsa_flag':0,'xrsb_flag':0},index=idx)
    pd.testing.assert_series_equal(features,build_features(science,now))
    assert meta['science_quality_flags_available'] is False
    assert meta['observations_through'] == '2026-01-03T23:59:00+00:00'

def test_operational_rejects_stale_or_sparse_data():
    import pandas as pd
    import pytest
    from realtime import operational_features
    rows=operational_sample()
    with pytest.raises(ValueError,match='stale'):
        operational_features(rows,pd.Timestamp('2026-01-04T01:00:00Z'))
    with pytest.raises(ValueError,match='coverage'):
        operational_features([r for r in rows if r['energy']!='0.05-0.4nm'],pd.Timestamp('2026-01-04T00:00:00Z'))
