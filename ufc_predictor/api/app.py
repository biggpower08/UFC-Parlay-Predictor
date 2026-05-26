"""FastAPI wrapper for predictions, search, feedback, and refresh."""

import math
import time
from datetime import date, datetime
from pathlib import Path
from uuid import UUID

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy import text

from ufc_predictor import __version__
from ufc_predictor.agents.orchestrator import FighterResolutionError, refresh_all, resolve_fighter
from ufc_predictor.db.schema import get_engine, init_db, using_postgres
from ufc_predictor.db.repository import resolve_name, save_prediction, search_fighters
from ufc_predictor.feedback.feedback_handler import save_feedback
from ufc_predictor.models.sklearn.predictor import model_available
from ufc_predictor.pipeline import run_prediction
from ufc_predictor.data.sync import get_sync_status
from ufc_predictor.rankings.generator import query_elo_history, query_rankings
from ufc_predictor.utils.helpers import normalize_name
from ufc_predictor.utils.logger import get_logger
from ufc_predictor.utils.weight_classes import detect_weight_class, same_weight_class

logger = get_logger(__name__)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_DIST_DIR = Path(__file__).resolve().parents[1] / "static_app"
HEALTH_CACHE_TTL_SECONDS = 45
_health_cache: dict | None = None
_health_cache_time = 0.0

app = FastAPI(title="UFC Predictor API", version=__version__)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PredictRequest(BaseModel):
    fighter_a: str
    fighter_b: str
    allow_scrape: bool = True
    confirmed_a: bool = False
    confirmed_b: bool = False
    allow_cross_division: bool = False
    debug: bool = False


class FeedbackRequest(BaseModel):
    prediction_id: str | None = None
    fighter_a: str
    fighter_b: str
    predicted_winner: str
    actual_winner: str | None = None
    confidence: float | None = None
    was_correct: bool
    user_notes: str | None = ""


@app.on_event("startup")
def startup() -> None:
    init_db()
    logger.info(
        "UFC Predictor API started version=%s database=%s",
        __version__,
        "postgres" if using_postgres() else "sqlite",
    )


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
    logger.info(
        "%s %s status=%s elapsed_ms=%s",
        request.method,
        request.url.path,
        response.status_code,
        elapsed_ms,
    )
    return response


@app.get("/api/health")
@app.get("/health")
def health(force: bool = False):
    global _health_cache, _health_cache_time
    now = time.monotonic()
    if not force and _health_cache and now - _health_cache_time < HEALTH_CACHE_TTL_SECONDS:
        return _health_cache

    start = time.perf_counter()
    db_ready = _database_ready()
    sklearn_ready = model_available()
    payload = {
        "ok": db_ready and sklearn_ready,
        "version": __version__,
        "database": "postgres" if using_postgres() else "sqlite",
        "database_ready": db_ready,
        "sklearn_model": sklearn_ready,
        "prediction_ready": db_ready and sklearn_ready,
        "frontend": {
            "available": FRONTEND_DIST_DIR.exists(),
            "path": str(FRONTEND_DIST_DIR),
        },
    }
    _health_cache = payload
    _health_cache_time = now
    _log_timing("health", start)
    return payload


@app.get("/api/version")
@app.get("/version")
def version():
    return {
        "name": "ufc-predictor-api",
        "version": __version__,
        "database": "postgres" if using_postgres() else "sqlite",
    }


@app.get("/api/fighters/search")
@app.get("/fighters/search")
def fighters_search(q: str, limit: int = 12):
    start = time.perf_counter()
    try:
        fighters = _timed_call("fighters.search.db", search_fighters, q, limit=limit)
        return {"fighters": _clean(fighters)}
    except Exception as exc:
        logger.exception("Fighter search failed query=%s", q)
        raise HTTPException(status_code=500, detail=f"Fighter search failed: {exc}") from exc
    finally:
        _log_timing("fighters.search", start, query=q, limit=limit)


@app.get("/api/fighters/resolve")
@app.get("/fighters/resolve")
def fighters_resolve(q: str):
    start = time.perf_counter()
    try:
        return _clean(_timed_call("fighters.resolve.db", resolve_name, q))
    except Exception as exc:
        logger.exception("Fighter resolve failed query=%s", q)
        raise HTTPException(status_code=500, detail=f"Fighter resolve failed: {exc}") from exc
    finally:
        _log_timing("fighters.resolve", start, query=q)


@app.get("/api/rankings")
@app.get("/rankings")
def rankings(type: str = "overall_current_elo", weight_class: str | None = None, limit: int = 50):
    start = time.perf_counter()
    try:
        return {"rankings": _clean(query_rankings(type, weight_class=weight_class, limit=limit))}
    except Exception as exc:
        logger.exception("Rankings query failed type=%s weight_class=%s", type, weight_class)
        raise HTTPException(status_code=500, detail=f"Rankings query failed: {exc}") from exc
    finally:
        _log_timing("rankings.query", start, type=type, weight_class=weight_class, limit=limit)


@app.get("/api/fighters/{fighter_key}/elo-history")
@app.get("/fighters/{fighter_key}/elo-history")
def fighter_elo_history(fighter_key: str, limit: int = 100):
    start = time.perf_counter()
    normalized = _resolve_fighter_history_key(fighter_key)
    if not normalized:
        raise HTTPException(status_code=404, detail="Fighter not found")
    try:
        return {"fighter": normalized, "elo_history": _clean(query_elo_history(normalized, limit=limit))}
    finally:
        _log_timing("fighters.elo_history", start, fighter=fighter_key, limit=limit)


@app.get("/api/internal/sync/status")
def internal_sync_status(source: str = "ufcstats"):
    start = time.perf_counter()
    try:
        return get_sync_status(source)
    except Exception as exc:
        logger.exception("Sync status query failed source=%s", source)
        raise HTTPException(status_code=500, detail=f"Sync status query failed: {exc}") from exc
    finally:
        _log_timing("sync.status", start, source=source)


@app.post("/api/predict")
@app.post("/predict")
def predict(request: PredictRequest):
    start = time.perf_counter()
    try:
        fighter_a = _timed_call(
            "predict.resolve_fighter_a",
            resolve_fighter,
            request.fighter_a,
            allow_scrape=request.allow_scrape,
            confirmed=request.confirmed_a,
        )
        fighter_b = _timed_call(
            "predict.resolve_fighter_b",
            resolve_fighter,
            request.fighter_b,
            allow_scrape=request.allow_scrape,
            confirmed=request.confirmed_b,
        )
    except FighterResolutionError as exc:
        raise HTTPException(status_code=409, detail=_clean(exc.payload)) from exc
    except Exception as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    class_a = detect_weight_class(fighter_a)
    class_b = detect_weight_class(fighter_b)
    if not request.allow_cross_division and not same_weight_class(class_a, class_b):
        raise HTTPException(
            status_code=422,
            detail={
                "status": "weight_class_mismatch",
                "message": (
                    f"{fighter_a.get('name', request.fighter_a)} is listed at {class_a}, "
                    f"while {fighter_b.get('name', request.fighter_b)} is listed at {class_b}. "
                    "Turn on cross-division matchups to continue."
                ),
                "fighter_a_weight_class": class_a,
                "fighter_b_weight_class": class_b,
            },
        )

    try:
        comparison, prediction, summary = _timed_call("predict.pipeline", run_prediction, fighter_a, fighter_b)
    except Exception as exc:
        logger.exception(
            "Prediction failed fighter_a=%s fighter_b=%s",
            fighter_a.get("name", request.fighter_a),
            fighter_b.get("name", request.fighter_b),
        )
        raise HTTPException(status_code=500, detail=f"Prediction failed: {type(exc).__name__}: {exc}") from exc

    payload = _clean(
        {
            "comparison": comparison,
            "prediction": prediction,
            "summary": summary,
        }
    )
    if not request.debug:
        payload["prediction"].pop("diagnostics", None)
    prediction_id = _timed_call(
        "predict.save_prediction",
        save_prediction,
        comparison["stats1"]["Name"],
        comparison["stats2"]["Name"],
        prediction,
        payload,
    )
    payload["prediction_id"] = prediction_id
    _log_timing("predict.total", start, fighter_a=comparison["stats1"]["Name"], fighter_b=comparison["stats2"]["Name"])
    return payload


@app.post("/api/compare")
@app.post("/compare")
def compare(request: PredictRequest):
    return predict(request)


@app.post("/api/feedback")
@app.post("/feedback")
def feedback(request: FeedbackRequest):
    start = time.perf_counter()
    try:
        record = _timed_call("feedback.save", save_feedback, request.dict())
        return {"saved": True, "feedback": _clean(record)}
    finally:
        _log_timing("feedback.total", start)


@app.post("/api/refresh")
@app.post("/refresh")
def refresh(force_refresh: bool = False):
    return {"refreshed": True, **refresh_all(force_refresh=force_refresh)}


@app.get("/", include_in_schema=False)
@app.head("/", include_in_schema=False)
def frontend_root():
    index_path = FRONTEND_DIST_DIR / "index.html"
    if index_path.exists():
        return HTMLResponse(index_path.read_text(encoding="utf-8"))
    return HTMLResponse(
        """
        <!doctype html>
        <html>
          <head><title>UFC Predictor</title></head>
          <body style="margin:0;background:#071019;color:#edf8ff;font-family:system-ui;display:grid;min-height:100vh;place-items:center;">
            <main style="max-width:720px;padding:32px;">
              <h1>UFC Predictor backend is online</h1>
              <p>The frontend build was not found on this Render deploy.</p>
              <p>Check the Render build log for the frontend build step, then redeploy.</p>
              <p><a style="color:#24f6ff" href="/api/health">Open API health</a></p>
            </main>
          </body>
        </html>
        """,
        status_code=503,
    )


if FRONTEND_DIST_DIR.exists():
    app.mount("/", StaticFiles(directory=FRONTEND_DIST_DIR, html=True), name="frontend")


def _clean(value):
    if isinstance(value, dict):
        return {k: _clean(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_clean(v) for v in value]
    if isinstance(value, tuple):
        return [_clean(v) for v in value]
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    try:
        import pandas as pd

        if pd.isna(value):
            return None
    except Exception:
        pass
    if isinstance(value, (datetime, date, UUID)):
        return str(value)
    return value


def _database_ready() -> bool:
    start = time.perf_counter()
    try:
        with get_engine().connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        logger.exception("Database health check failed")
        return False
    finally:
        _log_timing("health.database", start)


def _resolve_fighter_history_key(value: str) -> str | None:
    normalized = normalize_name(value)
    try:
        with get_engine().begin() as conn:
            row = conn.execute(
                text(
                    """
                    select normalized_name
                    from fighters
                    where normalized_name = :normalized
                       or lower(cast(id as text)) = lower(:raw)
                    limit 1
                    """
                ),
                {"normalized": normalized, "raw": value},
            ).mappings().fetchone()
        if row:
            return row["normalized_name"]
    except Exception:
        logger.exception("Fighter history key lookup failed value=%s", value)
    return normalized or None


def _timed_call(label: str, func, *args, **kwargs):
    start = time.perf_counter()
    try:
        return func(*args, **kwargs)
    finally:
        _log_timing(label, start)


def _log_timing(label: str, start: float, **fields) -> None:
    elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
    extra = " ".join(f"{key}={value}" for key, value in fields.items() if value is not None)
    logger.info("timing %s elapsed_ms=%s%s", label, elapsed_ms, f" {extra}" if extra else "")
