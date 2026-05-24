"""Initial model training from fight history."""

from ufc_predictor.config import settings
from ufc_predictor.data_sources.fights import load_fights
from ufc_predictor.features.feature_engineering import build_master_df, get_elo_tables
from ufc_predictor.features.matchup_builder import FEATURE_NAMES, build_training_dataset
from ufc_predictor.models.elo.elo_engine import export_elo_leaderboard
from ufc_predictor.models.sklearn.predictor import save_model, save_weights, train_pipeline
from ufc_predictor.utils.logger import get_logger

logger = get_logger(__name__)


def train():
    logger.info("Starting initial training")
    master = build_master_df()
    fights = load_fights()
    X, y = build_training_dataset(fights, master)
    pipeline, metrics = train_pipeline(X, y)
    save_model({"pipeline": pipeline, "feature_names": FEATURE_NAMES})
    save_weights(pipeline, metrics)
    if settings.EXPORT_ELO_ON_TRAIN:
        elo_data = get_elo_tables()
        export_elo_leaderboard(elo_data["elo_ratings"])
    logger.info("Training complete accuracy=%s", metrics.get("test_accuracy"))
    print(f"Trained on {metrics['n_samples']} samples, test accuracy {metrics['test_accuracy']:.1%}")
    print(f"Model -> {settings.LATEST_MODEL_PKL}")
    return pipeline, metrics


if __name__ == "__main__":
    train()
