"""NOAA measurement-based context; not a satellite failure or mission risk model."""
from datetime import datetime, timezone
import math

def parse_utc(value):
    parsed = datetime.fromisoformat(str(value).replace('Z','+00:00'))
    return parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed.astimezone(timezone.utc)

def read_observation(records, key, energy=None):
    found=[]
    for row in records:
        if not isinstance(row,dict) or (energy is not None and row.get('energy') != energy): continue
        try:
            val=float(row[key]); stamp=parse_utc(row['time_tag'])
            if math.isfinite(val) and val >= 0: found.append((stamp,val))
        except (KeyError,TypeError,ValueError,OverflowError): continue
    if not found: return None
    stamp,value=max(found,key=lambda x:x[0])
    return {'value':value,'time':stamp.isoformat()}

def fresh(obs, now, max_minutes):
    if not obs: return False
    try:
        age=(now-parse_utc(obs['time'])).total_seconds()
        return -300 <= age <= max_minutes*60 and math.isfinite(float(obs['value'])) and float(obs['value']) >= 0
    except (KeyError,ValueError,TypeError,OverflowError): return False

def evaluate_impacts(measurements, now):
    specs=[
      ('Communication disruption','xray',15,1e-5,'R1','GOES 0.1–0.8 nm X-ray flux','W/m²','M1 X-ray flux can disrupt sunlit-side HF radio. Effects depend on location and frequency.'),
      ('Navigation interference','kp',360,5,'G1','NOAA planetary Kp index','Kp','Geomagnetic storms can disturb the ionosphere and degrade GNSS accuracy; effects vary by location.'),
      ('Radiation exposure','protons',30,10,'S1','GOES ≥10 MeV proton flux','pfu','A solar radiation storm can increase particle exposure and upset spacecraft electronics; actual exposure depends on orbit and shielding.'),
      ('Operational effects','kp',360,5,'G1','NOAA planetary Kp index','Kp','Geomagnetic storms may increase low-Earth-orbit drag or affect spacecraft charging and orientation; mission effects vary.')]
    cards=[]
    for title,key,age,threshold,scale,label,unit,description in specs:
        obs=measurements.get(key)
        if not fresh(obs,now,age):
            cards.append({'title':title,'status':'Unavailable','basis':f'{label} is missing or stale.','explanation':'Current conditions cannot be assessed from this input.','time':obs.get('time') if obs else None})
        else:
            elevated=obs['value']>=threshold
            basis=f"{label}: {obs['value']:.2g} {unit}. " + (f'At or above the {scale} threshold.' if elevated else f'Below the {scale} threshold.')
            cards.append({'title':title,'status':'Elevated' if elevated else 'Below threshold','basis':basis,'explanation':description,'time':obs['time']})
    return cards

def parse_orbit(record, now):
    stamp=parse_utc(record['EPOCH']); age=(now-stamp).total_seconds()/86400
    inclination=float(record['INCLINATION']); motion=float(record['MEAN_MOTION']); cat=int(record['NORAD_CAT_ID'])
    if not math.isfinite(inclination) or not math.isfinite(motion) or motion<=0 or not 0<=inclination<=180 or age < -1: raise ValueError('Invalid orbital elements')
    return {'name':str(record['OBJECT_NAME']),'catalog_id':cat,'epoch':stamp.isoformat(),'age_days':round(age,2),'inclination':inclination,'orbits_per_day':motion,'status':'current' if age<=14 else 'stale'}

def evaluate_services(measurements, now):
    """Scale-based environmental context, never measured service outages."""
    cards=[]
    specs=[('hf','HF radio communications','xray',15,'W/m²',[1e-5,5e-5,1e-4,1e-3,2e-3],'R'),('gps','GPS & navigation','kp',360,'Kp',[5,6,7,8,9],'G'),('grid','Electric power grids','kp',360,'Kp',[5,6,7,8,9],'G'),('cables','Undersea communications','kp',360,'Kp',[5,6,7,8,9],'G')]
    for ident,title,key,age,unit,thresholds,prefix in specs:
        obs=measurements.get(key)
        valid=fresh(obs,now,age) and (key!='kp' or obs['value']<=9)
        level=sum(obs['value']>=v for v in thresholds) if valid else None
        status=('Below storm threshold' if level==0 else f'{prefix}{level} conditions') if valid else 'Unavailable'
        if ident=='hf':
            effects=['No R-scale blackout threshold reached. This does not rule out other radio disturbances.','Minor sunlit-side HF degradation and occasional loss of contact are possible.','Limited sunlit-side HF blackouts and loss of contact for tens of minutes are possible.','Wide-area sunlit-side HF blackouts lasting about an hour are possible.','Most sunlit-side HF communication may be lost for one to two hours.','Sunlit-side HF communication may be lost for several hours.']
            explanation=effects[level] if valid else 'Fresh X-ray observations are needed to assess sunlit-side radio conditions.'
            limitation='Applies to aviation, maritime and emergency HF links. Location, frequency and polar particle absorption are not assessed; this is not a measured blackout.'
            recommendation='Check current radio advisories and established backup communication procedures.'
        elif ident=='gps':
            explanation=('No geomagnetic storm threshold reached; local ionospheric interference is still possible.' if level==0 else 'Geomagnetic activity is elevated. Local ionospheric changes may affect navigation; Kp alone cannot establish signal degradation.' if level<3 else 'Intermittent satellite navigation problems are possible.' if level==3 else 'Satellite navigation may be degraded for hours.' if level==4 else 'Satellite navigation may be degraded for days.') if valid else 'Fresh geomagnetic observations are needed for environmental context.'
            limitation='Positioning error in metres cannot be calculated without local electron content, scintillation and receiver measurements.'
            recommendation='Check receiver integrity and local navigation advisories; use approved alternative navigation procedures when needed.'
        elif ident=='grid':
            effects=['No geomagnetic storm threshold reached; local induced currents are not measured.','Weak power-grid fluctuations are possible.','High-latitude systems may experience voltage alarms; long storms may stress transformers.','Voltage corrections may be needed and protection devices may trigger false alarms.','Widespread voltage-control problems and protection trips are possible.','Severe voltage-control problems, transformer damage and blackouts in some systems are possible.']
            explanation=effects[level] if valid else 'Fresh geomagnetic observations are needed for environmental context.'
            limitation='Kp does not give local induced current, transformer temperature or outage probability. Grid topology, geology and local electric fields are required.'
            recommendation='Consult grid-operator advisories and local geomagnetically induced-current monitoring.'
        else:
            explanation='Geomagnetic disturbances can induce voltage in cable power-feed conductors. Optical signals themselves are not directly affected. Actual service disruption cannot be inferred from Kp.'
            limitation='No validated cable damage threshold is available here. Cable route, ocean/ground conductivity, local magnetic variation and power-feed design are required. Repeater damage or internet outages are not predicted.'
            recommendation='Consult cable-operator power-feed telemetry and established engineering procedures.'
        cards.append({'id':ident,'title':title,'status':status,'value':obs['value'] if valid else None,'unit':unit,'time':obs.get('time') if obs else None,'scale_level':level,'assessment':'Environmental context only' if ident=='cables' else 'Estimated possible effects','explanation':explanation,'limitation':limitation,'recommendation':recommendation})
    return cards
