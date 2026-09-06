"""
Abstract search provider interface.
"""

from abc import ABC, abstractmethod
from typing import List
from app.services.search.models import SearchCandidate


class SearchProvider(ABC):
    """Abstract interface for reverse face search providers."""

    @abstractmethod
    async def search(self, image_path: str, artifact_dir: str) -> List[SearchCandidate]:
        """Search the web for content matching the provided face image."""
        pass

    @abstractmethod
    def provider_name(self) -> str:
        """Return unique provider identifier string."""
        pass
