"""User feedback collection and ingestion for retraining."""

import uuid
from datetime import datetime, timezone

import pandas as pd
from sqlalchemy import text

from ufc_predictor.config import settings
from ufc_predictor.db.schema import get_engine, init_db, using_postgres
from ufc_predictor.feedback.note_parser import assign_flags_to_fighters
from ufc_predictor.utils.helpers import normalize_name
from ufc_predictor.utils.logger import get_logger

logger = get_logger(__name__)

FEEDBACK_COLUMNS = [
    "prediction_id",
    "fighter_a",
    "fighter_b",
    "predicted_winner",
    "actual_winner",
    "confidence",
    "was_correct",
    "user_notes",
    "timestamp",
]


def _ensure_log_file():
    settings.DATA_FEEDBACK_DIR.mkdir(parents=True, exist_ok=True)
    path = settings.FEEDBACK_LOG_CSV
    if not path.is_file():
        pd.DataFrame(columns=FEEDBACK_COLUMNS).to_csv(path, index=False)
    return path


def load_feedback() -> pd.DataFrame:
    if using_postgres():
        init_db()
        return pd.read_sql_query("SELECT * FROM feedback", get_engine())

    path = _ensure_log_file()
    df = pd.read_csv(path)
    for col in FEEDBACK_COLUMNS:
        if col not in df.columns:
            df[col] = None
    return df


def save_feedback(record: dict) -> dict:
    row = {col: record.get(col) for col in FEEDBACK_COLUMNS}
    if not row.get("prediction_id"):
        row["prediction_id"] = str(uuid.uuid4())
    if not row.get("timestamp"):
        row["timestamp"] = datetime.now(timezone.utc).isoformat()

    if using_postgres():
        init_db()
        with get_engine().begin() as conn:
            conn.execute(
                text(
                    """
                    INSERT INTO feedback
                        (prediction_id, fighter_a, fighter_b, predicted_winner, actual_winner,
                         confidence, was_correct, user_notes, timestamp)
                    VALUES
                        (:prediction_id, :fighter_a, :fighter_b, :predicted_winner, :actual_winner,
                         :confidence, :was_correct, :user_notes, :timestamp)
                    """
                ),
                row,
            )
        logger.info("Feedback saved id=%s correct=%s", row["prediction_id"], row.get("was_correct"))
        return row

    path = _ensure_log_file()
    df = load_feedback()
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    df.to_csv(path, index=False)
    logger.info(
        "Feedback saved id=%s correct=%s",
        row["prediction_id"],
        row.get("was_correct"),
    )
    return row


def ingest_feedback(master_df) -> tuple:
    """
    Build supplemental X, y from incorrect predictions user corrected.
    y=1 when fighter_a (feature perspective) should win.
    """
    from ufc_predictor.features.matchup_builder import (
        build_matchup_features,
        features_to_vector,
        master_index_by_name,
    )

    fb = load_feedback()
    if fb.empty:
        return None, None

    wrong = fb[fb["was_correct"].astype(str).str.lower().isin(["false", "0", "n", "no"])]
    if wrong.empty:
        return None, None

    by_name = master_index_by_name(master_df)
    X_list, y_list = []

    for _, row in wrong.iterrows():
        a_name, b_name = row["fighter_a"], row["fighter_b"]
        actual = row["actual_winner"]
        a_key, b_key = normalize_name(a_name), normalize_name(b_name)
        if a_key not in by_name or b_key not in by_name:
            continue

        a_row, b_row = by_name[a_key], by_name[b_key]
        flags_a, flags_b = assign_flags_to_fighters(
            str(row.get("user_notes") or ""),
            a_name,
            b_name,
        )
        feats = build_matchup_features(a_row, b_row, flags_a, flags_b)
        label = 1 if normalize_name(actual) == a_key else 0
        X_list.append(features_to_vector(feats))
        y_list.append(label)

    if not X_list:
        return None, None
    import numpy as np

    return np.vstack(X_list), np.array(y_list, dtype=int)


def count_pending_retrain() -> int:
    """Feedback rows since last model train (all rows for now)."""
    return len(load_feedback())


def should_retrain() -> bool:
    return count_pending_retrain() >= settings.RETRAIN_FEEDBACK_THRESHOLD
