"""Guarded dedicated prop-model training entrypoint.

Training is intentionally blocked until credible source health and a
leakage-safe chronological dataset audit pass. Use --dry-run to inspect current
dataset readiness without writing artifacts.
"""

from __future__ import annotations

import json
import argparse

from ufc_predictor.config import settings
from ufc_predictor.training.dataset_builder import build_training_rows, load_fights_csv


def main() -> int:
    parser = argparse.ArgumentParser(description="Train dedicated prop models only after data readiness is proven.")
    parser.add_argument("--dry-run", action="store_true", help="Audit available training rows without training.")
    parser.add_argument("--input", default=str(settings.FIGHTS_CSV), help="Input fights CSV for readiness audit.")
    parser.add_argument("--source", default="csv", choices=["csv", "ufcstats_cache", "manual_html"])
    args = parser.parse_args()

    fights = load_fights_csv(args.input)
    _dataset, audit = build_training_rows(fights, source=args.source)
    print(json.dumps(audit.to_dict(), indent=2, default=str))
    print("Training blocked: credible source health and leakage-safe chronological data must be proven first.")
    return 0 if args.dry_run else 2


def train_prop_models() -> dict:
    raise RuntimeError(
        "Dedicated prop-model training is blocked until source health and training dataset readiness pass."
    )


if __name__ == "__main__":
    raise SystemExit(main())
