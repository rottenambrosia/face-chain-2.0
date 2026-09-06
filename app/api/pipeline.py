"""
Pipeline endpoints — the two core routes for the MVP.

POST /pipeline/run     — full pipeline: face detect → search → evidence → blockchain
POST /pipeline/verify  — re-verify a case's evidence against the on-chain record
"""

import logging
import shutil
from pathlib import Path

from fastapi import APIRouter, File, Request, UploadFile, HTTPException, Query
from pydantic import BaseModel

from app.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


class VerifyRequest(BaseModel):
    case_id: str


def get_pipeline(request: Request):
    """Retrieve pipeline from app state or lazy-initialize if lifespan was bypassed."""
    if hasattr(request.app.state, "pipeline") and request.app.state.pipeline:
        return request.app.state.pipeline
    from app.services.face.detector import FaceDetector
    from app.services.blockchain.client import BlockchainClient
    from app.services.pipeline_service import PipelineService
    pipeline = PipelineService(FaceDetector(), BlockchainClient())
    request.app.state.pipeline = pipeline
    return pipeline


@router.post("/run")
async def run_pipeline(
    request: Request,
    images: UploadFile = File(..., description="Face image (JPEG/PNG, max 10 MB)"),
    auto_select: bool = Query(True, description="Auto-select top search candidate"),
):
    """
    Run the full FaceChain pipeline end-to-end.

    1. Detect & encode face
    2. Search web via FaceCheck API
    3. Build deterministic evidence + SHA-256 hash
    4. Store hash on Polygon Amoy blockchain
    """
    # Validate file type
    if images.content_type not in ("image/jpeg", "image/png"):
        raise HTTPException(400, f"Unsupported image type: {images.content_type}. Use JPEG or PNG.")

    # Validate file size (10 MB)
    contents = await images.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(400, "Image exceeds 10 MB limit.")

    # Save upload to temp location
    import uuid

    upload_id = uuid.uuid4().hex[:8]
    upload_dir = settings.UPLOADS_DIR / upload_id
    upload_dir.mkdir(parents=True, exist_ok=True)

    suffix = ".jpg" if images.content_type == "image/jpeg" else ".png"
    image_path = str(upload_dir / f"original{suffix}")
    with open(image_path, "wb") as f:
        f.write(contents)

    logger.info(f"Saved upload to {image_path} ({len(contents)} bytes)")

    # Run pipeline
    pipeline = get_pipeline(request)
    try:
        result = await pipeline.run(image_path, auto_select=auto_select)
        return result
    except ValueError as e:
        raise HTTPException(422, str(e))
    except TimeoutError as e:
        raise HTTPException(504, str(e))
    except RuntimeError as e:
        raise HTTPException(502, str(e))
    except Exception as e:
        logger.error(f"Pipeline error: {e}", exc_info=True)
        raise HTTPException(500, f"Pipeline failed: {e}")


@router.post("/verify")
async def verify_evidence(body: VerifyRequest, request: Request):
    """
    Re-verify a case by recomputing the SHA-256 hash from the stored
    canonical JSON and comparing it with the on-chain record.
    """
    pipeline = get_pipeline(request)
    try:
        result = pipeline.verify(body.case_id)
        return result
    except FileNotFoundError as e:
        raise HTTPException(404, str(e))
    except Exception as e:
        logger.error(f"Verification error: {e}", exc_info=True)
        raise HTTPException(500, f"Verification failed: {e}")
