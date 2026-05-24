"""APScheduler jobs for data refresh and feedback-triggered retraining."""

from ufc_predictor.agents.orchestrator import refresh_all
from ufc_predictor.feedback.feedback_handler import should_retrain
from ufc_predictor.training.retrain import retrain_model
from ufc_predictor.utils.logger import get_logger

logger = get_logger(__name__)


def refresh_fights():
    logger.info("Scheduled fight refresh started")
    return refresh_all(force_refresh=True)


def retrain_if_needed():
    if not should_retrain():
        return {"retrained": False}
    _, metrics = retrain_model()
    return {"retrained": True, "metrics": metrics}


def sync_rankings():
    result = refresh_all(force_refresh=False)
    return {"synced": True, **result}


def create_scheduler():
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
    except ImportError as exc:
        raise RuntimeError("Install apscheduler to enable scheduled jobs") from exc

    scheduler = BackgroundScheduler(timezone="America/New_York")
    scheduler.add_job(refresh_fights, "cron", hour=3, minute=0, id="refresh_fights", replace_existing=True)
    scheduler.add_job(retrain_if_needed, "interval", hours=6, id="retrain_if_needed", replace_existing=True)
    scheduler.add_job(sync_rankings, "cron", day_of_week="sun", hour=4, minute=0, id="sync_rankings", replace_existing=True)
    return scheduler


def start_scheduler():
    scheduler = create_scheduler()
    scheduler.start()
    return scheduler
