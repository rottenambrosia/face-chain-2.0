"""
Canonical evidence builder and deterministic SHA-256 hasher.
"""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any

from app.services.evidence.models import EvidenceRecord


class EvidenceBuilder:
    """Builds reproducible canonical JSON records and generates cryptographic hashes."""

    @staticmethod
    def build(
        case_id: str,
        source_url: str,
        search_score: int,
        search_provider: str,
        face_confidence: float,
        artifact_dir: str,
    ) -> EvidenceRecord:
        """
        Build a deterministic canonical dictionary and compute its SHA-256 hash.

        Privacy Note: Biometric embeddings and raw image bytes are strictly excluded
        from the canonical evidence dictionary to ensure privacy and compliance.
        """
        canonical: Dict[str, Any] = {
            "case_id": case_id,
            "face_confidence": round(float(face_confidence), 4),
            "pipeline_version": "2.0.0",
            "search_provider": search_provider,
            "search_score": int(search_score),
            "source_url": source_url,
        }

        # Deterministic serialization: sorted keys, tight separators, ASCII safe
        canonical_str = json.dumps(
            canonical,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )

        evidence_hash = "0x" + hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()

        # Save to disk
        artifact_path = Path(artifact_dir)
        artifact_path.mkdir(parents=True, exist_ok=True)
        canonical_json_path = str(artifact_path / "evidence.json")
        with open(canonical_json_path, "w", encoding="utf-8") as f:
            f.write(canonical_str)

        created_at = datetime.now(timezone.utc).isoformat()

        return EvidenceRecord(
            case_id=case_id,
            evidence_hash=evidence_hash,
            canonical_json=canonical,
            canonical_json_path=canonical_json_path,
            ipfs_cid=None,
            created_at=created_at,
        )

    @staticmethod
    def recompute_hash(canonical_json_path: str) -> str:
        """Read saved canonical JSON file and recompute SHA-256 hash for verification."""
        path = Path(canonical_json_path)
        if not path.exists():
            raise FileNotFoundError(f"Canonical evidence JSON not found at {canonical_json_path}")

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        # Re-parse and re-serialize to ensure canonical format even if whitespace changed
        parsed = json.loads(content)
        canonical_str = json.dumps(
            parsed,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )
        return "0x" + hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()
