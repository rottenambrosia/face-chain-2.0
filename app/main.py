"""
FastAPI application factory.

Creates the app, registers routers, sets up CORS, and initializes
heavyweight resources (InsightFace model, DB, blockchain client) at startup.
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, Response
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

    # Load InsightFace model (or OpenCV fallback)
    face_detector = FaceDetector()
    logger.info("Face detection engine ready")

    # Blockchain client
    blockchain_client = BlockchainClient()
    contract_info = (
        settings.CONTRACT_ADDRESS[:12] + "…"
        if (settings.CONTRACT_ADDRESS and not settings.CONTRACT_ADDRESS.startswith("0xYour"))
        else "Local / Simulated"
    )
    logger.info(f"Blockchain client ready — contract: {contract_info}")

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

    # Root landing endpoint for browser visitors
    @app.get("/", include_in_schema=False)
    async def root(request: Request):
        accept = request.headers.get("accept", "")
        if "text/html" in accept:
            html_content = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>{settings.APP_NAME} Backend</title>
                <style>
                    body {{
                        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                        background: #0b0f19;
                        color: #f1f5f9;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        min-height: 100vh;
                        margin: 0;
                    }}
                    .card {{
                        background: #151d30;
                        border: 1px solid #23304c;
                        border-radius: 16px;
                        padding: 40px;
                        max-width: 580px;
                        width: 90%;
                        box-shadow: 0 12px 40px rgba(0,0,0,0.5);
                    }}
                    h1 {{
                        margin-top: 0;
                        color: #818cf8;
                        font-size: 1.8rem;
                        display: flex;
                        align-items: center;
                        gap: 12px;
                    }}
                    .badge {{
                        background: #065f46;
                        color: #34d399;
                        font-size: 0.75rem;
                        padding: 4px 10px;
                        border-radius: 12px;
                        font-weight: 600;
                    }}
                    p {{
                        color: #94a3b8;
                        line-height: 1.6;
                        margin-bottom: 24px;
                    }}
                    .links {{
                        display: flex;
                        flex-wrap: wrap;
                        gap: 12px;
                    }}
                    .btn {{
                        background: #4f46e5;
                        color: #ffffff;
                        text-decoration: none;
                        padding: 10px 18px;
                        border-radius: 8px;
                        font-weight: 500;
                        transition: background 0.15s;
                    }}
                    .btn:hover {{
                        background: #4338ca;
                    }}
                    .btn-secondary {{
                        background: #1e293b;
                        color: #cbd5e1;
                        border: 1px solid #334155;
                    }}
                    .btn-secondary:hover {{
                        background: #334155;
                    }}
                </style>
            </head>
            <body>
                <div class="card">
                    <h1>🔗 {settings.APP_NAME} <span class="badge">ONLINE</span></h1>
                    <p>
                        The backend API is running successfully. Pipeline routes are available at
                        <code>/api/v1</code>. Access the interactive Swagger documentation or launch the Streamlit frontend.
                    </p>
                    <div class="links">
                        <a class="btn" href="/docs">Swagger API Docs</a>
                        <a class="btn" href="http://localhost:8501" target="_blank">Streamlit Frontend (Port 8501)</a>
                        <a class="btn btn-secondary" href="/api/v1/health">Health Status</a>
                    </div>
                </div>
            </body>
            </html>
            """
            return HTMLResponse(content=html_content)

        return {
            "app": settings.APP_NAME,
            "status": "online",
            "version": "2.0.0",
            "docs": "/docs",
            "frontend": "http://localhost:8501",
            "health": "/api/v1/health",
        }

    # Favicon handler to avoid 404 logs
    @app.get("/favicon.ico", include_in_schema=False)
    async def favicon():
        return Response(status_code=204)

    # Register API routes
    app.include_router(api_router, prefix="/api/v1")

    return app


app = create_app()
