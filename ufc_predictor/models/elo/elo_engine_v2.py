"""Versioned placeholder for the creator's updated Elo engine.

This module intentionally delegates to v1 until the new creator logic is
provided and reviewed. Keeping it separate lets us compare old vs new outputs
before changing production predictions.
"""

from ufc_predictor.models.elo.elo_engine import compute_elo_ratings as compute_elo_ratings_v1

ELO_ENGINE_VERSION = "v2-pending"


def compute_elo_ratings(fights_df, initial_elo=None, k_factor=None):
    return compute_elo_ratings_v1(
        fights_df,
        initial_elo=initial_elo,
        k_factor=k_factor,
    )
