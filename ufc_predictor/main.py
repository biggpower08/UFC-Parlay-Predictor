"""
UFC Predictor — lightweight CLI entry point.
"""

import uuid

from ufc_predictor.config import settings
from ufc_predictor.features.feature_engineering import build_master_df
from ufc_predictor.feedback.feedback_handler import save_feedback, should_retrain
from ufc_predictor.models.sklearn.predictor import model_available
from ufc_predictor.pipeline import print_report, run_prediction, select_fighters
from ufc_predictor.training.retrain import retrain_model
from ufc_predictor.utils.logger import get_logger

logger = get_logger(__name__)


def collect_feedback(fighter_a, fighter_b, prediction):
    """Prompt user after each prediction."""
    winner = prediction["winner"]
    conf = prediction.get("confidence", 0.5)
    print(f"\nPrediction: {winner}")
    print(f"Confidence: {conf:.1%}")

    accurate = input("\nWas this prediction accurate? (y/n): ").strip().lower()
    was_correct = accurate in ("y", "yes")

    record = {
        "prediction_id": str(uuid.uuid4()),
        "fighter_a": fighter_a,
        "fighter_b": fighter_b,
        "predicted_winner": winner,
        "actual_winner": winner if was_correct else "",
        "confidence": round(conf, 4),
        "was_correct": was_correct,
        "user_notes": "",
    }

    if not was_correct:
        record["actual_winner"] = input("Actual winner: ").strip()
        record["user_notes"] = input("Why was it wrong? (notes): ").strip()

    save_feedback(record)
    logger.info("Feedback recorded correct=%s", was_correct)


def maybe_retrain():
    if should_retrain():
        print(
            f"\nFeedback threshold ({settings.RETRAIN_FEEDBACK_THRESHOLD}) reached — retraining..."
        )
        retrain_model()
        logger.info("Auto-retrain completed")


def main():
    print("=== UFC Predictor ===\n")
    settings.LOGS_DIR.mkdir(parents=True, exist_ok=True)
    settings.DATA_FEEDBACK_DIR.mkdir(parents=True, exist_ok=True)

    logger.info("Application started")
    print("Loading fighters (stats + rankings + Elo)...")
    df = build_master_df()
    print(f"Loaded {len(df)} fighters")

    if not model_available():
        print("No model yet. Run: python -m ufc_predictor.training.train\n")

    from ufc_predictor.utils.helpers import find_name_column

    f1, f2 = select_fighters(df)
    ncol = find_name_column(df)
    name_a, name_b = f1[ncol], f2[ncol]

    comparison, prediction, summary = run_prediction(f1, f2)
    print_report(comparison, prediction, summary)
    collect_feedback(name_a, name_b, prediction)
    maybe_retrain()


if __name__ == "__main__":
    main()
