"""
SQLAlchemy ORM models for FaceChain 2.0.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Text, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Case(Base):
    """Represents a single pipeline run case."""

    __tablename__ = "cases"

    id = Column(String, primary_key=True)  # e.g., "fc_20260906_a1b2c3"
    status = Column(
        String, default="created"
    )  # created | face_detected | searching | evidence_built | committed | verified | failed | no_matches
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Face detection
    image_path = Column(String)  # path to uploaded original
    aligned_face_path = Column(String, nullable=True)
    face_confidence = Column(Float, nullable=True)
    face_bbox_json = Column(Text, nullable=True)  # JSON string "[x1, y1, x2, y2]"

    # Search
    search_provider = Column(String, nullable=True)
    search_raw_response_path = Column(String, nullable=True)
    selected_candidate_json = Column(Text, nullable=True)  # JSON of selected SearchCandidate
    candidates_count = Column(Integer, default=0)

    # Evidence
    evidence_hash = Column(String, nullable=True)  # "0x..."
    evidence_json_path = Column(String, nullable=True)
    ipfs_cid = Column(String, nullable=True)

    # Blockchain
    tx_hash = Column(String, nullable=True)
    block_number = Column(Integer, nullable=True)
    contract_address = Column(String, nullable=True)

    # Error
    error_message = Column(Text, nullable=True)
