"""
FastAPI application factory.

Creates the app, registers routers, sets up CORS, and initializes
heavyweight resources (InsightFace model, DB, blockchain client) at startup.
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.api.router import api_router
from app.services.db.database import init_db
from app.services.face.detector import FaceDetector
from app.services.blockchain.client import BlockchainClient
from app.services.pipeline_service import PipelineService

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle."""
    # ── Startup ──────────────────────────────────────────────────────────
    logger.info("🔗 FaceChain 2.0 starting up …")

    # Ensure data directories exist
    settings.UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    settings.ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    # Initialise database
    init_db()
    logger.info("Database initialised")

    # Load InsightFace model (slow — do once)
    face_detector = FaceDetector()
    logger.info("InsightFace model loaded")

    # Blockchain client
    blockchain_client = BlockchainClient()
    logger.info(f"Blockchain client ready — contract {settings.CONTRACT_ADDRESS[:10]}…")

    # Wire up the pipeline service as app-level state
    app.state.pipeline = PipelineService(face_detector, blockchain_client)
    logger.info("Pipeline service ready")

    yield

    # ── Shutdown ─────────────────────────────────────────────────────────
    logger.info("FaceChain 2.0 shutting down")


def create_app() -> FastAPI:
    """Build and return the FastAPI application."""
    app = FastAPI(
        title=settings.APP_NAME,
        version="2.0.0",
        description="Face Scan → Web Search → Blockchain Verification Pipeline",
        lifespan=lifespan,
    )

    # CORS — allow Streamlit (port 8501) and local dev
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Serve saved artifacts as static files
    data_dir = Path(settings.DATA_DIR)
    data_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/static", StaticFiles(directory=str(data_dir)), name="static")

    # Register routes
    app.include_router(api_router, prefix="/api/v1")

    return app


app = create_app()
