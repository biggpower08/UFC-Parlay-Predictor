# API Contract

Base URLs:

- Local development: `http://localhost:8000`
- Hosted production: configured in the frontend with `NEXT_PUBLIC_API_BASE`

## Health

`GET /health`

```json
{
  "ok": true,
  "database": "postgres",
  "database_ready": true,
  "sklearn_model": true,
  "prediction_ready": true,
  "frontend": {
    "available": true
  }
}
```

## Fighter Search

`GET /fighters/search?q=islam`

Returns live backend matches. The frontend should not use mocked fighter data.

## Fighter Resolve

`GET /fighters/resolve?q=poatan`

Resolves partial names, nicknames, and close matches.

## Predict

`POST /predict`

```json
{
  "fighter_a": "Islam Makhachev",
  "fighter_b": "Alex Pereira",
  "allow_scrape": true,
  "confirmed_a": true,
  "confirmed_b": true,
  "allow_cross_division": false
}
```

Returns:

- `comparison`
- `prediction`
- `summary`
- `prediction_id`
