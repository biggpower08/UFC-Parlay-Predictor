"""Compare current Elo output with the staged v2 Elo engine."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ufc_predictor.data_sources.fights import load_fights
from ufc_predictor.models.elo.elo_engine import compute_elo_ratings as compute_v1
from ufc_predictor.models.elo.elo_engine_v2 import ELO_ENGINE_VERSION, compute_elo_ratings as compute_v2
from ufc_predictor.utils.helpers import normalize_name


def compare(limit: int = 25) -> pd.DataFrame:
    fights = load_fights(force_refresh=False)
    _f1, ratings_v1, _p1, _s1 = compute_v1(fights)
    _f2, ratings_v2, _p2, _s2 = compute_v2(fights)
    rows = []
    for fighter in sorted(set(ratings_v1) | set(ratings_v2)):
        old = ratings_v1.get(fighter)
        new = ratings_v2.get(fighter)
        if old is None or new is None:
            delta = None
        else:
            delta = round(new - old, 2)
        rows.append(
            {
                "fighter": fighter,
                "normalized_name": normalize_name(fighter),
                "elo_v1": old,
                ELO_ENGINE_VERSION: new,
                "delta": delta,
            }
        )
    out = pd.DataFrame(rows).sort_values("delta", key=lambda s: s.abs(), ascending=False, na_position="last")
    return out.head(limit)


def main() -> int:
    result = compare()
    print(result.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
