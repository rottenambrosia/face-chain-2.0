"""
Mock Search Provider for offline testing, demos, and fallback operation.
"""

import json
import logging
from pathlib import Path
from typing import List

from app.services.search.base import SearchProvider
from app.services.search.models import SearchCandidate

logger = logging.getLogger(__name__)


class MockSearchProvider(SearchProvider):
    """Provides realistic simulated search results for reverse face lookup."""

    def provider_name(self) -> str:
        return "mock"

    async def search(self, image_path: str, artifact_dir: str) -> List[SearchCandidate]:
        logger.info("Using MockSearchProvider to return realistic demo candidates")

        # High quality realistic social media / web matches
        mock_candidates = [
            SearchCandidate(
                rank=1,
                score=94,
                source_url="https://x.com/techfounder/status/1789234509123847291",
                thumbnail_b64="",
                provider="mock",
                raw_data={
                    "url": "https://x.com/techfounder/status/1789234509123847291",
                    "score": 94,
                    "platform": "Twitter / X",
                    "author": "@techfounder",
                    "date": "2024-05-11T14:22:00Z",
                    "caption": "Keynote presentation at Global AI & Web3 Summit",
                },
            ),
            SearchCandidate(
                rank=2,
                score=88,
                source_url="https://www.linkedin.com/posts/dr-alex-chen_ai-future-verification-activity-71938491209384",
                thumbnail_b64="",
                provider="mock",
                raw_data={
                    "url": "https://www.linkedin.com/posts/dr-alex-chen_ai-future-verification-activity-71938491209384",
                    "score": 88,
                    "platform": "LinkedIn",
                    "author": "Dr. Alex Chen",
                    "date": "2024-05-09T09:15:00Z",
                    "caption": "Excited to share our latest research on digital provenance",
                },
            ),
            SearchCandidate(
                rank=3,
                score=76,
                source_url="https://instagram.com/p/C6z89bOtyKl/",
                thumbnail_b64="",
                provider="mock",
                raw_data={
                    "url": "https://instagram.com/p/C6z89bOtyKl/",
                    "score": 76,
                    "platform": "Instagram",
                    "author": "alex_innovates",
                    "date": "2024-05-04T18:40:00Z",
                    "caption": "Hackathon weekend kickoff!",
                },
            ),
        ]

        # Save raw response artifact
        raw_path = Path(artifact_dir) / "search_raw_response.json"
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        raw_dict = {
            "provider": "mock",
            "count": len(mock_candidates),
            "items": [c.raw_data for c in mock_candidates],
        }
        raw_path.write_text(json.dumps(raw_dict, indent=2))

        return mock_candidates
