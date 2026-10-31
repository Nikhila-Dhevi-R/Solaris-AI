# Solaris AI

A local space-weather dashboard using React, Vite, Tailwind CSS and FastAPI. All forecasts are informational shadow-mode research outputs, not operational warnings.

## Current state and important limitations

The dashboard displays NOAA SWPC GOES primary X-ray measurements, measured flux history and recent NOAA-issued products. Issued products are not necessarily active alerts. Observations are cached in memory for two minutes (alerts for five); the displayed observation timestamp and stale status matter. Internet access to NOAA is required. Satellite-specific assessments are unavailable: orbital elements, radiation and geomagnetic measurements, and mission-specific models are not yet connected.

**Live forecasts are experimental shadow-mode research outputs.** The supplied Version 6 bundle and its supporting artifacts are stored in `backend/models/`. The bundle has been checked against the supplied file's SHA-256, schema, model type and frozen thresholds. Load only trusted joblib files: joblib uses pickle and can execute code. Inference requires scikit-learn 1.6.1, the version recorded in the artifact.

`backend/features.py` implements the notebook's completed-hour transformation for science-quality, per-band flagged observations; `backend/inference.py` and `backend/model_service.py` apply input checks, the saved preprocessing and forest, and the saved calibrator. `POST /api/forecast/features` performs genuine shadow-mode inference on a caller-supplied mapping of the 38 named features. This endpoint cannot independently verify their provenance, timing, quality, or that they represent live conditions; its result is not an operational warning. It rejects excessive missing features and inadequate reported coverage, and reports features outside historical ranges. `GET /api/forecast` uses NOAA SWPC's operational two-channel XRS flux to construct the 38 features from completed prior-hour bins and trailing windows. It uses the fitted model and saved calibrator, but the operational feed does not provide the science-quality flags used in training. Coverage measures usable reported flux, not science-quality data; no flags are invented. The app requires at least 80% coverage in both channels over each 1-, 24-, and 72-hour window, fresh observations, and a single identified satellite; inadequate inputs are rejected. The science-quality and operational products differ, and historical replay, calibration, and equivalence remain unvalidated. The display labels the result experimental and not an operational warning.

The supplied historical 2020–2024 test table records 79.21% accuracy, 88.13% recall, 59.99% precision and 0.901 ROC AUC at the frozen 0.20594365951619512 threshold. These describe hourly forecast windows in that test period; they are not guarantees for present conditions or event-level accuracy. The published test results varied substantially by year, and test data had been previously observed. The risk boundaries are 0.02756797277329327 and 0.36999108243721823. No retraining or threshold changes were made.

## Windows setup

Requires Python 3.10–3.13 and Node.js 20.19+ or 22.12+. In PowerShell from this directory:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python -m pip install -r backend\requirements.txt
npm install --prefix frontend
```

Open two PowerShell terminals in the project directory:

```powershell
.\.venv\Scripts\python -m uvicorn app:app --app-dir backend --host 127.0.0.1 --port 8000
```

```powershell
npm run dev --prefix frontend
```

Visit http://127.0.0.1:5173. The Vite development proxy forwards `/api` to the local backend. API documentation is at http://127.0.0.1:8000/docs. The optional frontend configuration is described in `.env.example`; if needed copy it to `frontend/.env`. No hosting configuration or deployment is required.

## Architecture and sources

- `backend/app.py`: FastAPI endpoints, NOAA retrieval, cache, timestamps and unavailable states.
- `backend/features.py` and `backend/inference.py`: Version 6 feature/inference components and an explicitly experimental operational-data adapter.
- `frontend/src`: responsive dashboard, navigation, chart filters, status indicators and NOAA messages.
- `backend/models`: intended storage for the verified artifact.
- Sources: https://services.swpc.noaa.gov/json/goes/primary/xrays-7-day.json and https://services.swpc.noaa.gov/products/alerts.json.

The measured current X-ray class is based on the GOES long channel and is not a forecast. SWPC data can be delayed, revised, or missing. When NOAA or the backend is unavailable the UI shows unavailable status; it does not synthesize data.

## Tests

```powershell
$env:PYTHONPATH='backend'
.\.venv\Scripts\python -m pytest backend\tests -q
npm run build --prefix frontend
```

The automated suite checks threshold boundaries, flux classification, unavailable forecasts, UTC completed-hour features, rejection of missing quality flags and API input validation. Full historical replay, live feature equivalence, and true satellite-risk assessment remain incomplete.
