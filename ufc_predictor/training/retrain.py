"""Retrain with fight history + user feedback + parsed note features."""

import numpy as np

from ufc_predictor.config import settings
from ufc_predictor.data_sources.fights import load_fights
from ufc_predictor.features.feature_engineering import build_master_df, get_elo_tables
from ufc_predictor.features.matchup_builder import FEATURE_NAMES, build_training_dataset
from ufc_predictor.feedback.feedback_handler import ingest_feedback, load_feedback
from ufc_predictor.models.elo.elo_engine import export_elo_leaderboard
from ufc_predictor.models.sklearn.predictor import save_model, save_weights, train_pipeline
from ufc_predictor.utils.logger import get_logger

logger = get_logger(__name__)


def retrain_model():
    """
    Load historical fights, merge feedback corrections and note flags, retrain sklearn.
    Optionally refresh Elo export.
    """
    logger.info("Retrain started")
    master = build_master_df(force_refresh=True)
    fights = load_fights()
    X_hist, y_hist = build_training_dataset(fights, master)

    parts_x = [X_hist]
    parts_y = [y_hist]

    if settings.USE_FEEDBACK_IN_TRAINING:
        X_fb, y_fb = ingest_feedback(master)
        if X_fb is not None and len(y_fb) > 0:
            parts_x.append(X_fb)
            parts_y.append(y_fb)
            logger.info("Merged %s feedback samples", len(y_fb))

    X = np.vstack(parts_x)
    y = np.concatenate(parts_y)

    pipeline, metrics = train_pipeline(X, y)
    save_model({"pipeline": pipeline, "feature_names": FEATURE_NAMES})
    save_weights(pipeline, metrics)

    if settings.EXPORT_ELO_ON_TRAIN:
        export_elo_leaderboard(get_elo_tables()["elo_ratings"])

    fb_count = len(load_feedback())
    metrics["feedback_rows"] = fb_count
    logger.info("Retrain complete samples=%s accuracy=%s", len(y), metrics["test_accuracy"])
    print(f"Retrained on {len(y)} samples (feedback rows in log: {fb_count})")
    print(f"Test accuracy: {metrics['test_accuracy']:.1%}")
    print(f"Saved -> {settings.LATEST_MODEL_PKL}")
    return pipeline, metrics


if __name__ == "__main__":
    retrain_model()
