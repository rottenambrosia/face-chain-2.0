"""
Unit tests for Evidence Construction, Canonical JSON, and SHA-256 Hashing.
"""

import json
import tempfile
from pathlib import Path
from app.services.evidence.builder import EvidenceBuilder


def test_evidence_builder_deterministic():
    """Verify that evidence hashing is strictly deterministic across multiple runs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        rec1 = EvidenceBuilder.build(
            case_id="fc_test_001",
            source_url="https://x.com/example/status/12345",
            search_score=95,
            search_provider="facecheck",
            face_confidence=0.991234,
            artifact_dir=tmpdir,
        )

        rec2 = EvidenceBuilder.build(
            case_id="fc_test_001",
            source_url="https://x.com/example/status/12345",
            search_score=95,
            search_provider="facecheck",
            face_confidence=0.991234,
            artifact_dir=tmpdir,
        )

        assert rec1.evidence_hash == rec2.evidence_hash
        assert rec1.evidence_hash.startswith("0x")
        assert len(rec1.evidence_hash) == 66  # "0x" + 64 hex characters


def test_evidence_recompute_match():
    """Verify that recompute_hash reproduces the exact same hash from saved file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        rec = EvidenceBuilder.build(
            case_id="fc_test_002",
            source_url="https://linkedin.com/posts/test",
            search_score=88,
            search_provider="mock",
            face_confidence=0.95,
            artifact_dir=tmpdir,
        )

        recomputed = EvidenceBuilder.recompute_hash(rec.canonical_json_path)
        assert recomputed == rec.evidence_hash


def test_evidence_tamper_detection():
    """Verify that altering even a single field in the canonical JSON changes the hash."""
    with tempfile.TemporaryDirectory() as tmpdir:
        rec = EvidenceBuilder.build(
            case_id="fc_test_003",
            source_url="https://instagram.com/p/test",
            search_score=80,
            search_provider="mock",
            face_confidence=0.92,
            artifact_dir=tmpdir,
        )

        # Alter file content on disk
        with open(rec.canonical_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        data["search_score"] = 99  # Tamper with score
        with open(rec.canonical_json_path, "w", encoding="utf-8") as f:
            json.dump(data, f)

        tampered_hash = EvidenceBuilder.recompute_hash(rec.canonical_json_path)
        assert tampered_hash != rec.evidence_hash
