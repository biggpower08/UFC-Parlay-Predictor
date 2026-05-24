# Backend

The production backend engine lives in `ufc_predictor/`.

This folder documents how the backend is launched in production. The current
deployment entrypoint is:

```powershell
alembic upgrade head && uvicorn ufc_predictor.api.app:app --host 0.0.0.0 --port $PORT
```

For local development:

```powershell
python -m uvicorn ufc_predictor.api.app:app --host 127.0.0.1 --port 8000
```

Set `UFC_PREDICTOR_DATA_DIR` when the runtime needs data stored outside the
package folder.

Production environment variables:

```text
DATABASE_URL
SUPABASE_URL
SUPABASE_SERVICE_KEY
UFC_PREDICTOR_DATA_DIR
FRONTEND_ORIGINS
```
