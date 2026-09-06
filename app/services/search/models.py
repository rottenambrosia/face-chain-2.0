"""
Search module data structures.
"""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class SearchCandidate:
    """Represents a matched social media or web candidate discovered during reverse face search."""

    rank: int
    score: int  # Match confidence score 0-100
    source_url: str  # URL where the face was discovered
    thumbnail_b64: str  # Base64-encoded thumbnail or image URL
    provider: str  # Search provider name e.g. "facecheck" or "mock"
    raw_data: Dict[str, Any]  # Complete raw dictionary from API response
