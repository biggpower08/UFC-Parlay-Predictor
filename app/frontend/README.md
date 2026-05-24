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

- Deploy this folder to Vercel.
- Set `NEXT_PUBLIC_API_URL` to the hosted Render backend URL.
- Set `NEXT_PUBLIC_SUPABASE_URL` to the Supabase project URL.
- Set `NEXT_PUBLIC_SUPABASE_ANON_KEY` to the Supabase anon key.
- Leave `NEXT_PUBLIC_API_BASE` empty in production unless you intentionally want the local proxy.
