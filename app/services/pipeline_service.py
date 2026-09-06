"""
Pipeline Service — Orchestrates the end-to-end flow:
Face Detection → Web Search → Evidence Hashing → Blockchain Verification
"""

import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional

from app.config import settings
from app.services.blockchain.client import BlockchainClient
from app.services.db.database import SessionLocal
from app.services.db import crud
from app.services.evidence.builder import EvidenceBuilder
from app.services.evidence.ipfs import IPFSClient
from app.services.face.detector import FaceDetector
from app.services.search.base import SearchProvider
from app.services.search.facecheck import FaceCheckProvider
from app.services.search.mock import MockSearchProvider

logger = logging.getLogger(__name__)


class PipelineService:
    """End-to-end orchestrator for FaceChain 2.0."""

    def __init__(self, face_detector: FaceDetector, blockchain_client: BlockchainClient):
        self.face_detector = face_detector
        self.blockchain_client = blockchain_client

    def _get_search_provider(self) -> SearchProvider:
        """Select configured search provider with intelligent fallback."""
        if settings.SEARCH_PROVIDER == "facecheck" and settings.FACECHECK_API_TOKEN:
            return FaceCheckProvider()
        return MockSearchProvider()

    async def run(self, image_path: str, auto_select: bool = True) -> Dict[str, Any]:
        """
        Execute the full pipeline for an input face image.
        """
        timestamp_str = datetime.now(timezone.utc).strftime("%Y%m%d")
        case_id = f"fc_{timestamp_str}_{uuid.uuid4().hex[:8]}"
        artifact_dir = str(settings.ARTIFACTS_DIR / case_id)
        Path(artifact_dir).mkdir(parents=True, exist_ok=True)

        logger.info("Starting pipeline for case %s (image: %s)", case_id, image_path)

        db = SessionLocal()
        try:
            crud.create_case(db, case_id=case_id, image_path=image_path)

            # ── 1. Face Detection & Encoding ─────────────────────────────────
            logger.info("[%s] Step 1: Face Detection & Embedding", case_id)
            face_res = self.face_detector.detect_and_embed(image_path, artifact_dir)

            crud.update_case(
                db,
                case_id,
                status="face_detected",
                aligned_face_path=face_res.aligned_face_path,
                face_confidence=face_res.confidence,
                face_bbox_json=json.dumps(face_res.bbox),
            )

            # ── 2. Web / Social Media Reverse Search ─────────────────────────
            logger.info("[%s] Step 2: Web / Social Media Search", case_id)
            provider = self._get_search_provider()
            crud.update_case(db, case_id, status="searching", search_provider=provider.provider_name())

            search_input = face_res.aligned_face_path or image_path
            try:
                candidates = await provider.search(search_input, artifact_dir)
            except Exception as e:
                logger.warning("[%s] Provider %s failed (%s). Falling back to MockSearchProvider.", case_id, provider.provider_name(), e)
                provider = MockSearchProvider()
                candidates = await provider.search(search_input, artifact_dir)

            if not candidates:
                crud.update_case(db, case_id, status="no_matches", candidates_count=0)
                return {
                    "case_id": case_id,
                    "status": "no_matches",
                    "face": {
                        "detected": True,
                        "confidence": face_res.confidence,
                        "bbox": face_res.bbox,
                        "aligned_face_path": face_res.aligned_face_path,
                    },
                    "search": {
                        "provider": provider.provider_name(),
                        "candidates_found": 0,
                        "selected": None,
                    },
                    "evidence": None,
                    "blockchain": None,
                }

            top_candidate = candidates[0]
            crud.update_case(
                db,
                case_id,
                candidates_count=len(candidates),
                selected_candidate_json=json.dumps(top_candidate.raw_data),
            )

            # ── 3. Evidence Construction & Cryptographic Hashing ─────────────
            logger.info("[%s] Step 3: Canonical Evidence Construction", case_id)
            crud.update_case(db, case_id, status="evidence_built")

            evidence_rec = EvidenceBuilder.build(
                case_id=case_id,
                source_url=top_candidate.source_url,
                search_score=top_candidate.score,
                search_provider=provider.provider_name(),
                face_confidence=face_res.confidence,
                artifact_dir=artifact_dir,
            )

            # Optional IPFS pinning
            ipfs_cid = await IPFSClient.pin_json(evidence_rec.canonical_json, case_id)
            crud.update_case(
                db,
                case_id,
                evidence_hash=evidence_rec.evidence_hash,
                evidence_json_path=evidence_rec.canonical_json_path,
                ipfs_cid=ipfs_cid,
            )

            # ── 4. Blockchain Anchoring ──────────────────────────────────────
            logger.info("[%s] Step 4: Blockchain Anchoring", case_id)
            metadata_ref = ipfs_cid or case_id
            chain_rec = self.blockchain_client.store_evidence(
                case_id=case_id,
                evidence_hash=evidence_rec.evidence_hash,
                metadata_ref=metadata_ref,
            )

            crud.update_case(
                db,
                case_id,
                status="committed",
                tx_hash=chain_rec.tx_hash,
                block_number=chain_rec.block_number,
                contract_address=chain_rec.contract_address,
            )

            logger.info("[%s] Pipeline completed successfully! Tx: %s", case_id, chain_rec.tx_hash)

            return {
                "case_id": case_id,
                "status": "completed",
                "face": {
                    "detected": True,
                    "confidence": face_res.confidence,
                    "bbox": face_res.bbox,
                    "aligned_face_path": face_res.aligned_face_path,
                },
                "search": {
                    "provider": provider.provider_name(),
                    "candidates_found": len(candidates),
                    "selected": {
                        "rank": top_candidate.rank,
                        "score": top_candidate.score,
                        "source_url": top_candidate.source_url,
                    },
                    "all_candidates": [
                        {
                            "rank": c.rank,
                            "score": c.score,
                            "source_url": c.source_url,
                            "raw_data": c.raw_data,
                        }
                        for c in candidates
                    ],
                },
                "evidence": {
                    "hash": evidence_rec.evidence_hash,
                    "canonical_json_path": evidence_rec.canonical_json_path,
                    "ipfs_cid": ipfs_cid,
                },
                "blockchain": {
                    "tx_hash": chain_rec.tx_hash,
                    "block_number": chain_rec.block_number,
                    "explorer_url": chain_rec.explorer_url,
                    "network": chain_rec.network,
                },
            }

        except Exception as e:
            logger.error("[%s] Pipeline error: %s", case_id, e, exc_info=True)
            crud.update_case(db, case_id, status="failed", error_message=str(e))
            raise
        finally:
            db.close()

    def verify(self, case_id: str) -> Dict[str, Any]:
        """
        Re-verify a previously processed case:
        1. Read stored canonical evidence JSON from disk
        2. Recompute SHA-256 hash
        3. Query on-chain record from smart contract
        4. Detect whether evidence has been tampered with
        """
        db = SessionLocal()
        try:
            case = crud.get_case(db, case_id)
            if not case:
                raise FileNotFoundError(f"Case ID {case_id} not found in database.")

            if not case.evidence_json_path:
                raise FileNotFoundError(f"No evidence record recorded for case {case_id}.")

            # Recompute local hash from stored canonical evidence file
            recomputed_hash = EvidenceBuilder.recompute_hash(case.evidence_json_path)

            # Query on-chain record
            on_chain_rec = self.blockchain_client.get_evidence(case_id)
            on_chain_hash = on_chain_rec["evidence_hash"]

            match = recomputed_hash.lower() == on_chain_hash.lower()
            tamper_detected = not match

            status = "verified" if match else "tampered"
            crud.update_case(db, case_id, status=status)

            return {
                "case_id": case_id,
                "recomputed_hash": recomputed_hash,
                "on_chain_hash": on_chain_hash,
                "match": match,
                "tamper_detected": tamper_detected,
                "on_chain_timestamp": on_chain_rec.get("timestamp", 0),
                "verification_time": datetime.now(timezone.utc).isoformat(),
            }
        finally:
            db.close()
