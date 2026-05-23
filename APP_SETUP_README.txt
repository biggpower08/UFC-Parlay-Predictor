UFC Predictor PWA files
=======================

Quick launch during development:

1. Open PowerShell in this folder.
2. Run:
   .\Start-UFC-Predictor.ps1

Build the installable PWA:

1. Open PowerShell in this folder.
2. Run:
   .\Build-UFC-Predictor-App.ps1
3. The production web build will be created by Next.js.
   For real users, deploy ufc_predictor\ui to Vercel.

What the app now does:

- Searches by full fighter name.
- Searches by partial fighter name.
- Searches by nickname when the nickname exists in the database.
- If the app is not sure, it asks you to confirm the closest real fighter.
- If it cannot recognize the entry at all, it asks for a full name.
- If the full name is not in the local database, the backend can try web scraping.
- UFCStats scraping can fill in core stat fields such as reach, stance, striking, takedown, and submission stats.

Important:

This is now a PWA-first project, not an Electron-first desktop app.
Real users should eventually open the hosted website and install it to their phone or desktop home screen.
