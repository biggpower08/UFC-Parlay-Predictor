# Model Data Source Plan

## Plain-English Summary
Supabase remains the production database. Kaggle and other downloaded CSVs are raw training inputs only: they live locally, feed normalization/training jobs, and are never required for the deployed app to run.

## Source Roles
- Production runtime: Supabase/Postgres and bundled small model artifacts.
- Training inputs: local CSVs under `data/imports/` or `ufc_predictor/data/imports/`.
- Normalized training outputs: generated under processed/import folders and not committed unless explicitly approved.
- Live UFCStats: optional source-health/diagnostic path only, not required for model training or runtime.

## Supported Local Sources
- Kaggle UFC fight forecast / gold modeling datasets.
- Kaggle ultimate UFC datasets.
- Kaggle fight/fighter stats datasets.
- Kaggle betting odds datasets, only for future odds work when timestamps are trusted.
- Greco-style UFCStats CSV exports when manually provided.
- Existing project raw/processed local data.

## Import Rules
- Raw downloaded data is never committed.
- Training rows must include event dates or a clearly documented experimental ordering.
- Current-fight outcome stats can be labels, not pre-fight features.
- Duplicate or mirrored fight rows must stay inside the same chronological split.
- Source contribution and missingness reports must be regenerated after import changes.

## Runtime Rules
- The deployed app must work without local Kaggle files.
- If a model needs raw CSVs only during training, that is fine.
- If runtime needs a model, commit a small safe artifact or store normalized data in Supabase.
- Do not require paid API keys or live scrapers for startup.
