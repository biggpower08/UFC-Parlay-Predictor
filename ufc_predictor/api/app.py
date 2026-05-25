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

from ufc_predictor import __version__
from ufc_predictor.agents.orchestrator import FighterResolutionError, refresh_all, resolve_fighter
from ufc_predictor.db.schema import init_db, using_postgres
from ufc_predictor.db.repository import resolve_name, save_prediction, search_fighters
from ufc_predictor.feedback.feedback_handler import save_feedback
from ufc_predictor.models.sklearn.predictor import model_available
from ufc_predictor.pipeline import run_prediction
from ufc_predictor.utils.logger import get_logger
from ufc_predictor.utils.weight_classes import detect_weight_class, same_weight_class

logger = get_logger(__name__)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_DIST_DIR = PROJECT_ROOT / "app" / "frontend" / "out"

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
def health():
    return {
        "ok": True,
        "version": __version__,
        "database": "postgres" if using_postgres() else "sqlite",
        "sklearn_model": model_available(),
        "frontend": {
            "available": FRONTEND_DIST_DIR.exists(),
            "path": str(FRONTEND_DIST_DIR),
        },
    }


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
    try:
        return {"fighters": _clean(search_fighters(q, limit=limit))}
    except Exception as exc:
        logger.exception("Fighter search failed query=%s", q)
        raise HTTPException(status_code=500, detail=f"Fighter search failed: {exc}") from exc


@app.get("/api/fighters/resolve")
@app.get("/fighters/resolve")
def fighters_resolve(q: str):
    try:
        return _clean(resolve_name(q))
    except Exception as exc:
        logger.exception("Fighter resolve failed query=%s", q)
        raise HTTPException(status_code=500, detail=f"Fighter resolve failed: {exc}") from exc


@app.post("/api/predict")
@app.post("/predict")
def predict(request: PredictRequest):
    try:
        fighter_a = resolve_fighter(
            request.fighter_a,
            allow_scrape=request.allow_scrape,
            confirmed=request.confirmed_a,
        )
        fighter_b = resolve_fighter(
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

    comparison, prediction, summary = run_prediction(fighter_a, fighter_b)
    payload = _clean(
        {
            "comparison": comparison,
            "prediction": prediction,
            "summary": summary,
        }
    )
    prediction_id = save_prediction(
        comparison["stats1"]["Name"],
        comparison["stats2"]["Name"],
        prediction,
        payload,
    )
    payload["prediction_id"] = prediction_id
    return payload


@app.post("/api/compare")
@app.post("/compare")
def compare(request: PredictRequest):
    return predict(request)


@app.post("/api/feedback")
@app.post("/feedback")
def feedback(request: FeedbackRequest):
    record = save_feedback(request.dict())
    return {"saved": True, "feedback": _clean(record)}


@app.post("/api/refresh")
@app.post("/refresh")
def refresh(force_refresh: bool = False):
    return {"refreshed": True, **refresh_all(force_refresh=force_refresh)}


@app.get("/", include_in_schema=False)
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
