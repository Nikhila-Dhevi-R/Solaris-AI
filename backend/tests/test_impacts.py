from datetime import datetime, timezone, timedelta
from impacts import evaluate_impacts, read_observation, parse_orbit

NOW = datetime(2026, 11, 4, 12, tzinfo=timezone.utc)

def observation(value, minutes=0):
    return {'value': value, 'time': (NOW-timedelta(minutes=minutes)).isoformat()}

def test_noaa_thresholds_drive_distinct_measured_indicators():
    cards=evaluate_impacts({'xray':observation(1e-5),'kp':observation(5),'protons':observation(10)},NOW)
    assert [c['status'] for c in cards] == ['Elevated', 'Elevated', 'Elevated', 'Elevated']
    assert 'R1' in cards[0]['basis'] and 'G1' in cards[1]['basis'] and 'S1' in cards[2]['basis']

def test_stale_and_missing_measurements_are_not_called_low():
    cards=evaluate_impacts({'xray':observation(1e-7,60),'kp':None,'protons':observation(1,120)},NOW)
    assert all(c['status'] == 'Unavailable' for c in cards)

def test_proton_reader_selects_exact_energy_and_rejects_negative_flux():
    records=[{'time_tag':'2026-11-04T11:55:00Z','energy':'>=100 MeV','flux':100}, {'time_tag':'2026-11-04T11:56:00Z','energy':'>=10 MeV','flux':-1}, {'time_tag':'2026-11-04T11:54:00Z','energy':'>=10 MeV','flux':1.2}]
    assert read_observation(records,'flux',energy='>=10 MeV')['value'] == 1.2

def test_orbit_element_age_and_missing_data():
    rec={'OBJECT_NAME':'Example','NORAD_CAT_ID':25544,'EPOCH':'2026-11-01T12:00:00','INCLINATION':51.6,'MEAN_MOTION':15.5}
    result=parse_orbit(rec,NOW)
    assert result['status']=='current' and result['catalog_id']==25544 and result['age_days']==3
    assert parse_orbit({**rec,'EPOCH':'2026-10-01T12:00:00'},NOW)['status']=='stale'

def test_satellite_endpoint_preserves_independent_data_on_source_failure(monkeypatch):
    from fastapi.testclient import TestClient
    from fastapi import HTTPException
    import app as app_module
    async def fake_noaa(path, ttl=120):
        if 'protons' in path: raise HTTPException(503, 'offline')
        now=datetime.now(timezone.utc).isoformat()
        if 'xrays' in path: return [{'time_tag':now,'energy':'0.1-0.8nm','flux':1e-5}]
        return [{'time_tag':now,'Kp':5}]
    async def fake_orbit(cat): raise ValueError('offline')
    monkeypatch.setattr(app_module,'get_noaa',fake_noaa)
    monkeypatch.setattr(app_module,'get_orbit',fake_orbit)
    data=TestClient(app_module.app).get('/api/satellites').json()
    assert data['status']=='available' and data['items']==[]
    assert [x['status'] for x in data['impacts']]==['Elevated','Elevated','Unavailable','Elevated']

def test_service_effects_follow_measurements_and_keep_cable_unknown():
    from impacts import evaluate_services
    cards=evaluate_services({'xray':observation(1e-4),'kp':observation(9)},NOW)
    assert cards[0]['status']=='R3 conditions'
    assert cards[2]['status']=='G5 conditions'
    assert 'blackouts' in cards[2]['explanation']
    assert cards[3]['assessment']=='Environmental context only'
    assert 'not predicted' in cards[3]['limitation']
    assert all(c['value'] is None for c in evaluate_services({},NOW))
    assert all(c['status']=='Unavailable' for c in evaluate_services({'xray':observation(1e-3,20),'kp':observation(5,361)},NOW))
    assert evaluate_services({'kp':observation(10)},NOW)[2]['status']=='Unavailable'
