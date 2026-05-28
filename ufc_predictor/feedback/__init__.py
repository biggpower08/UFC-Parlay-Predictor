from ufc_predictor.feedback.note_parser import parse_user_notes

__all__ = [
    "save_feedback",
    "load_feedback",
    "ingest_feedback",
    "should_retrain",
    "parse_user_notes",
]


def __getattr__(name):
    if name in {"save_feedback", "load_feedback", "ingest_feedback", "should_retrain"}:
        from ufc_predictor.feedback import feedback_handler

        return getattr(feedback_handler, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
