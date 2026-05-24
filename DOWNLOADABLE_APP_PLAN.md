# UFC Predictor: Downloadable App Plan

The project is now moving toward a PWA-first architecture. Do not use Electron
for the current production path.

## Final User Experience

Users should not install Python, Node, npm, Ollama, or run local scripts.

They should:

1. Open the hosted UFC Predictor website.
2. Tap "Install" or "Add to Home Screen."
3. Use it like an app on phone or desktop.

## Architecture

```text
Installable PWA
    -> FastAPI backend
    -> shared database
```

## Recommended Hosting

- Frontend: Vercel
- Backend: Render or Railway
- Database later: Supabase

## Current Local Testing

Backend:

```powershell
cd C:\Users\trish\OneDrive\Desktop\mma-ai
python -m uvicorn ufc_predictor.api.app:app --host 127.0.0.1 --port 8000
```

Frontend:

```powershell
cd C:\Users\trish\OneDrive\Desktop\mma-ai\ufc_predictor\ui
npm run dev
```

Open:

```text
http://localhost:5173
```

## Do Not Prioritize Yet

- Electron installers
- Tauri installers
- App Store builds
- New prediction features

Those come after the hosted PWA is stable.
