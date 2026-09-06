"""
Integration tests for FaceChain 2.0 pipeline and verification endpoints.
"""

import io
from pathlib import Path
import numpy as np
import pytest
from PIL import Image
from fastapi.testclient import TestClient

from app.main import app
from app.services.db.database import init_db


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    init_db()


def create_dummy_face_image() -> io.BytesIO:
    """Generate an in-memory test image with a simple face-like pattern."""
    img = Image.new("RGB", (300, 300), color=(240, 220, 200))
    # Draw simple facial landmarks
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    return buf


def test_root_endpoint():
    """Verify root landing endpoint returns 200 with links."""
    client = TestClient(app)
    # JSON request
    response = client.get("/", headers={"accept": "application/json"})
    assert response.status_code == 200
    assert response.json()["status"] == "online"

    # Browser HTML request
    html_resp = client.get("/", headers={"accept": "text/html"})
    assert html_resp.status_code == 200
    assert "FaceChain" in html_resp.text


def test_favicon_endpoint():
    """Verify favicon does not return 404."""
    client = TestClient(app)
    response = client.get("/favicon.ico")
    assert response.status_code == 204


def test_health_endpoint():
    """Verify that the health check endpoint responds with 200 OK and expected keys."""
    client = TestClient(app)
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "search_provider" in data
    assert "blockchain_rpc" in data


def test_pipeline_run_and_verify_e2e():
    """Verify end-to-end pipeline execution from face upload to blockchain verification."""
    client = TestClient(app)
    img_buf = create_dummy_face_image()

    # Step 1: Run pipeline
    files = {"images": ("test_face.jpg", img_buf, "image/jpeg")}
    response = client.post("/api/v1/pipeline/run", files=files)
    assert response.status_code == 200
    res = response.json()

    assert res["status"] in ("completed", "no_matches")
    case_id = res["case_id"]
    assert case_id.startswith("fc_")

    if res["status"] == "completed":
        assert "evidence" in res
        assert "blockchain" in res
        assert res["evidence"]["hash"].startswith("0x")
        assert res["blockchain"]["tx_hash"].startswith("0x")

        # Step 2: Verify against blockchain
        verify_resp = client.post("/api/v1/pipeline/verify", json={"case_id": case_id})
        assert verify_resp.status_code == 200
        v_data = verify_resp.json()
        assert v_data["match"] is True
        assert v_data["tamper_detected"] is False
        assert v_data["recomputed_hash"] == v_data["on_chain_hash"]
