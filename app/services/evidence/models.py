"""
Evidence module data structures.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class EvidenceRecord:
    """Represents a finalized canonical evidence bundle and its cryptographic hash."""

    case_id: str
    evidence_hash: str  # "0x" + 64 hex characters (SHA-256)
    canonical_json: Dict[str, Any]  # Exactly what was hashed
    canonical_json_path: str  # Path to saved JSON file
    ipfs_cid: Optional[str] = None  # IPFS / Pinata CID if pinned
    created_at: Optional[str] = None  # ISO 8601 UTC timestamp
