"""Shim — Elo export moved to ufc_predictor package."""
from ufc_predictor.models.elo.elo_engine import compute_elo_ratings, export_elo_leaderboard
from ufc_predictor.data_sources.fights import load_fights

if __name__ == "__main__":
    fights = load_fights()
    _, elo_ratings, peak, _ = compute_elo_ratings(fights)
    export_elo_leaderboard(elo_ratings)
    print(f"Exported Elo for {len(elo_ratings)} fighters.")
