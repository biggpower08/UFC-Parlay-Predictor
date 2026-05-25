# Frontend

This is the installable PWA frontend.

Local development:

```powershell
npm install
npm run dev
```

The app runs at:

```text
http://localhost:5173
```

Production:

- Preferred: Render builds this folder as a static export and FastAPI serves `app/frontend/out`.
- Vercel is optional as a backup, not the primary production host.
- The app calls same-origin `/api` first, so the single Render app does not need cross-site API wiring.
