# Architecture Audit

## Current High-Priority Issues Found

1. The project had competing app directions: local scripts, PWA deployment, and old desktop packaging artifacts.
2. Generated folders such as `node_modules`, `.next`, `dist`, and `release` were mixed into the working tree.
3. Frontend source lived under `ufc_predictor/ui`, which blurred backend engine code and product UI code.
4. ELO refresh existed as reusable Python logic, but not as a cron-friendly production script.
5. The frontend used live backend calls, but error handling and search layering needed hardening.

## Production Direction

The app is now organized around a PWA-first architecture.

```text
app/frontend  -> installable Next.js PWA
ufc_predictor -> Python prediction backend engine
scripts       -> automation and maintenance scripts
docs          -> build/run/deploy docs
```

No Electron path is active.

## Why PWA

- Users install from browser on phone or desktop.
- No Python or Node install for end users.
- Easier updates than native desktop installers.
- Deploys cleanly to Vercel + Render/Railway.

## Backend

FastAPI app:

```text
ufc_predictor.api.app:app
```

The backend owns:

- fighter search
- name resolution
- predictions
- ELO values
- feedback
- refresh jobs

## Frontend

Canonical frontend source:

```text
app/frontend
```

The frontend must call backend APIs only. It should not carry mocked fighter,
prediction, or ELO data.
