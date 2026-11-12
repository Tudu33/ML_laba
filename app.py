"""
FastAPI приложение для сервиса предсказаний сетевых атак (ЛР4).
"""
import hashlib
import logging
import os
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, Any
from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from prometheus_fastapi_instrumentator import Instrumentator

# Настройка структурированного логирования
logging.basicConfig(
    level=logging.INFO,
    format='{"time": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s", "request_id": "%(request_id)s"}'
)
logger = logging.getLogger(__name__)

# Абсолютные пути
BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "baseline_pipeline.joblib"
MODEL_VERSION = "lab2-v1"
API_TOKEN = os.getenv("API_TOKEN", "demo-secret-token-123")

app_state = {"model": None, "model_loaded": False}
limiter = Limiter(key_func=get_remote_address)

def load_model() -> bool:
    try:
        if not MODEL_PATH.exists():
            logger.error(f"Model file not found at {MODEL_PATH}", extra={"request_id": "startup"})
            return False
        with open(MODEL_PATH, "rb") as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
        expected_hash = "2877a05b7d902249780b0c1df36760d29aa3d95ff57be962c01b7018c1128bd3"
        if file_hash != expected_hash:
            logger.error(f"Model hash mismatch!", extra={"request_id": "startup"})
            return False
        app_state["model"] = joblib.load(MODEL_PATH)
        app_state["model_loaded"] = True
        logger.info("Model loaded and verified successfully.", extra={"request_id": "startup"})
        return True
    except Exception as e:
        logger.error(f"Failed to load model: {e}", extra={"request_id": "startup"})
        return False

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application...", extra={"request_id": "startup"})
    load_model()
    yield
    logger.info("Shutting down application...", extra={"request_id": "shutdown"})

app = FastAPI(title="ML Security API", version="1.0.0", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, lambda req, exc: JSONResponse(
    status_code=429, content={"error": "Rate limit exceeded. Try again later."}
))

# Подключаем метрики Prometheus (автоматически собирает http_requests_total, http_request_duration_seconds)
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

static_dir = BASE_DIR / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

async def verify_token(request: Request):
    token = request.headers.get("X-API-Token")
    if not token or token != API_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid or missing API token")
    return token

@app.get("/")
async def root():
    index_path = BASE_DIR / "static" / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return {"message": "ML Security API", "docs": "/docs"}

@app.get("/health")
async def health_check():
    if not app_state["model_loaded"]:
        raise HTTPException(status_code=503, detail="Service not ready: model not loaded")
    return {"status": "healthy", "model_version": MODEL_VERSION}

@app.post("/predict")
@limiter.limit("10/minute")
async def predict(
    request: Request,
    payload: Dict[str, Any],
    token: str = Depends(verify_token)
):
    request_id = str(uuid.uuid4())
    log_extra = {"request_id": request_id}
    logger.info("Prediction request received", extra=log_extra)
    
    if not app_state["model_loaded"]:
        logger.error("Service not ready", extra=log_extra)
        raise HTTPException(status_code=503, detail="Service not ready")
    
    try:
        df = pd.DataFrame([payload])
        from src.predict import predict_traffic
        prediction = predict_traffic(df)
        
        logger.info(f"Prediction successful: {int(prediction[0])}", extra=log_extra)
        return {
            "prediction": int(prediction[0]),
            "model_version": MODEL_VERSION,
            "request_id": request_id
        }
    except ValueError as ve:
        logger.warning(f"Validation failed: {ve}", extra=log_extra)
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Internal error: {e}", extra=log_extra)
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001  # nosec B104)
